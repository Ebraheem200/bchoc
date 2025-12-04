# bchoc/commands/verify_cmd.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from bchoc.storage import iter_blocks, Header, _hash_block  # type: ignore[attr-defined]

ZERO32 = b"\x00" * 32
TERMINAL_STATES = {"DISPOSED", "DESTROYED", "RELEASED"}

@dataclass
class BlockInfo:
    header: Header
    data: bytes
    hash: bytes  # sha256(header+data)

def _collect_blocks() -> List[BlockInfo]:
    blocks: List[BlockInfo] = []
    for hdr, data in iter_blocks():
        h = _hash_block(hdr.pack(), data)  # type: ignore[attr-defined]
        blocks.append(BlockInfo(hdr, data, h))
    return blocks

def _print_header(tx_count: int) -> None:
    print(f"> Transactions in blockchain: {tx_count}")

def _error_parent_not_found(bad_hash: bytes, tx_count: int) -> int:
    _print_header(tx_count)
    print("> State of blockchain: ERROR")
    print(f"> Bad block: {bad_hash.hex()}")
    print("> Parent block: NOT FOUND")
    return 1

def _error_duplicate_parent(bad_hash: bytes, parent_hash: bytes, tx_count: int) -> int:
    _print_header(tx_count)
    print("> State of blockchain: ERROR")
    print(f"> Bad block: {bad_hash.hex()}")
    print(f"> Parent block: {parent_hash.hex()}")
    print("> Two blocks were found with the same parent.")
    return 1

def _error_checksum(bad_hash: bytes, tx_count: int) -> int:
    _print_header(tx_count)
    print("> State of blockchain: ERROR")
    print(f"> Bad block: {bad_hash.hex()}")
    print("> Block contents do not match block checksum.")
    return 1

def _error_sequence(bad_hash: bytes, tx_count: int) -> int:
    _print_header(tx_count)
    print("> State of blockchain: ERROR")
    print(f"> Bad block: {bad_hash.hex()}")
    print("> Item checked out or checked in after removal from chain.")
    return 1

def _check_genesis(blocks: List[BlockInfo]) -> Optional[int]:
    tx_count = len(blocks)
    if not blocks:
        # No blocks at all -> treat as error on "missing genesis"
        dummy_hash = b"\x00" * 32
        return _error_checksum(dummy_hash, tx_count)

    g = blocks[0]
    hdr, data = g.header, g.data

    state = hdr.state.rstrip(b"\x00").decode("ascii", errors="replace")
    if not (
        hdr.prev_hash == ZERO32
        and hdr.timestamp == 0.0
        and hdr.case_id == b"0" * 32
        and hdr.item_id == b"0" * 32
        and state == "INITIAL"
        and hdr.creator == b"\x00" * 12
        and hdr.owner == b"\x00" * 12
        and data == b"Initial block\x00"
        and hdr.data_length == len(data)
    ):
        # Any deviation from the expected genesis layout: call it a checksum/content error
        return _error_checksum(g.hash, tx_count)

    return None


def _check_hash_links(blocks: List[BlockInfo]) -> Optional[int]:
    tx_count = len(blocks)
    # Map: block_hash -> index
    hash_to_index: Dict[bytes, int] = {}
    for idx, bi in enumerate(blocks):
        hash_to_index[bi.hash] = idx

    # Map: parent_hash -> child_hash (to detect duplicates)
    parent_to_child: Dict[bytes, bytes] = {}

    # Start from second block
    for idx in range(1, len(blocks)):
        bi = blocks[idx]
        parent_hash = bi.header.prev_hash

        # prev_hash must not be all zeros for non-genesis blocks
        if parent_hash == ZERO32:
            return _error_parent_not_found(bi.hash, tx_count)

        if parent_hash not in hash_to_index:
            # No earlier block with this hash
            return _error_parent_not_found(bi.hash, tx_count)

        # Check for duplicate parent (branching)
        if parent_hash in parent_to_child:
            # Another block already uses this same parent_hash
            first_child = parent_to_child[parent_hash]
            # We report the "second" child as the bad one
            return _error_duplicate_parent(bi.hash, parent_hash, tx_count)

        parent_to_child[parent_hash] = bi.hash

    return None

def _check_item_sequences(blocks: List[BlockInfo]) -> Optional[int]:
    tx_count = len(blocks)
    # item_id_enc -> (current_state:str, removed:bool, seen_any:bool)
    item_state: Dict[bytes, Tuple[str, bool, bool]] = {}

    # Skip genesis (index 0)
    for idx in range(1, len(blocks)):
        bi = blocks[idx]
        hdr = bi.header
        state = hdr.state.rstrip(b"\x00").decode("ascii", errors="replace")

        if state == "INITIAL":
            # Should not appear again, but ignore if it does
            continue

        enc_item = hdr.item_id
        current, removed, seen_any = item_state.get(enc_item, ("", False, False))

        # First time we see this item
        if not seen_any:
            # First action must be CHECKEDIN, otherwise invalid sequence
            if state != "CHECKEDIN":
                return _error_sequence(bi.hash, tx_count)
            item_state[enc_item] = ("CHECKEDIN", False, True)
            continue

        # If already removed, any further action is invalid
        if removed:
            return _error_sequence(bi.hash, tx_count)

        # Non-terminal transitions
        if state == "CHECKEDIN":
            # Must come from CHECKEDOUT
            if current != "CHECKEDOUT":
                return _error_sequence(bi.hash, tx_count)
            item_state[enc_item] = ("CHECKEDIN", False, True)
        elif state == "CHECKEDOUT":
            # Must come from CHECKEDIN
            if current != "CHECKEDIN":
                return _error_sequence(bi.hash, tx_count)
            item_state[enc_item] = ("CHECKEDOUT", False, True)
        elif state in TERMINAL_STATES:
            # Terminal must come from CHECKEDIN and only once
            if current != "CHECKEDIN":
                return _error_sequence(bi.hash, tx_count)
            item_state[enc_item] = (state, True, True)
        else:
            # Unknown state: treat as content error
            return _error_checksum(bi.hash, tx_count)

    return None

def run_verify(args) -> int:
    # Collect all blocks and hashes
    blocks = _collect_blocks()
    tx_count = len(blocks)

    # 1) Genesis sanity
    ec = _check_genesis(blocks)
    if ec is not None:
        return ec

    # 2) Hash link / parent checks
    ec = _check_hash_links(blocks)
    if ec is not None:
        return ec

    # 3) Per-item state-sequence rules
    ec = _check_item_sequences(blocks)
    if ec is not None:
        return ec

    # If everything passes, report CLEAN
    _print_header(tx_count)
    print("> State of blockchain: CLEAN")
    return 0
