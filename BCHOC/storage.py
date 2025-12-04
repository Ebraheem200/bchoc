# bchoc/storage.py
"""
Low-level binary I/O for the blockchain file.

- init_file(): create file + INITIAL (genesis) block if missing
- iter_blocks(): iterate (Header, data) over all blocks
- append_block(): append a new block linked by prev_hash
- get_latest_items(): map latest state per item_id
"""

import os
import struct
import time
import hashlib
from dataclasses import dataclass
from typing import Iterator, Tuple, Dict, Optional

from .env import BLOCKCHAIN_FILE

# ---------------- Binary layout ----------------
#
# 32s  d  32s     32s     12s    12s     12s     I
# prev ts case_id item_id state  creator owner  data_length
# ---------------------------------------------------------

HEADER_FMT = "32s d 32s 32s 12s 12s 12s I"
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def pad_state(name: str) -> bytes:
    """Pad a state name (ASCII) to 12 bytes with NULs."""
    raw = name.encode("ascii")
    if len(raw) > 12:
        raise ValueError("state name too long")
    return raw + b"\x00" * (12 - len(raw))

def _zero32() -> bytes:
    return b"\x00" * 32

def _hash_block(header_bytes: bytes, data: bytes) -> bytes:
    """Compute SHA-256 hash of header+data (full block)."""
    h = hashlib.sha256()
    h.update(header_bytes)
    h.update(data)
    return h.digest()

def resolve_path(path: Optional[str] = None) -> str:
    """Blockchain file path from argument or env or default."""
    if path is not None:
        return path
    return BLOCKCHAIN_FILE

# ---------------- Header dataclass ----------------
@dataclass
class Header:
    prev_hash: bytes
    timestamp: float
    case_id: bytes
    item_id: bytes
    state: bytes
    creator: bytes
    owner: bytes
    data_length: int

    def pack(self) -> bytes:
        return struct.pack(
            HEADER_FMT,
            self.prev_hash,
            self.timestamp,
            self.case_id,
            self.item_id,
            self.state,
            self.creator,
            self.owner,
            self.data_length,
        )

    @staticmethod
    def unpack(buf: bytes) -> "Header":
        if len(buf) != HEADER_SIZE:
            raise ValueError(f"header must be {HEADER_SIZE} bytes")
        fields = struct.unpack(HEADER_FMT, buf)
        return Header(*fields)

# ---------------- Genesis (INITIAL) block ----------------
def _genesis_block() -> Tuple[Header, bytes]:
    """
    INITIAL block:
    - prev_hash = 32 zero bytes
    - timestamp = 0.0
    - case_id   = b"0"*32   (ASCII '0', not NULs)
    - item_id   = b"0"*32
    - state     = "INITIAL" (padded to 12 bytes)
    - creator   = 12 zero bytes
    - owner     = 12 zero bytes
    - data      = b"Initial block\\0"
    """
    prev_hash = _zero32()
    timestamp = 0.0
    case_id = b"0" * 32
    item_id = b"0" * 32
    state = pad_state("INITIAL")
    creator = b"\x00" * 12
    owner = b"\x00" * 12
    data = b"Initial block\x00"
    header = Header(
        prev_hash=prev_hash,
        timestamp=timestamp,
        case_id=case_id,
        item_id=item_id,
        state=state,
        creator=creator,
        owner=owner,
        data_length=len(data),
    )
    return header, data

# ---------------- Public API ----------------
def init_file(path: Optional[str] = None) -> Tuple[bool, str]:
    p = resolve_path(path)

    if not os.path.exists(p):
        header, data = _genesis_block()
        with open(p, "wb") as f:
            f.write(header.pack())
            f.write(data)
        return True, "Blockchain file not found. Created INITIAL block."

    with open(p, "rb") as f:
        first = f.read(HEADER_SIZE)
        if len(first) != HEADER_SIZE:
            raise SystemExit("Corrupted blockchain file (short header).")
        hdr = Header.unpack(first)
        state = hdr.state.rstrip(b"\x00").decode("ascii", errors="replace")
        if state != "INITIAL" or hdr.case_id != b"0" * 32 or hdr.item_id != b"0" * 32:
            raise SystemExit("Invalid genesis block (not INITIAL with zero IDs).")

    return False, "Blockchain file found with INITIAL block."

def iter_blocks(path: Optional[str] = None) -> Iterator[Tuple[Header, bytes]]:
    p = resolve_path(path)
    with open(p, "rb") as f:
        while True:
            header_bytes = f.read(HEADER_SIZE)
            if not header_bytes:
                break
            if len(header_bytes) != HEADER_SIZE:
                raise SystemExit("Corrupted blockchain file (trailing header).")
            hdr = Header.unpack(header_bytes)
            data = f.read(hdr.data_length)
            if len(data) != hdr.data_length:
                raise SystemExit("Corrupted blockchain file (truncated data).")
            yield hdr, data

def append_block(
    *,
    case_id: bytes,
    item_id: bytes,
    state: str,
    creator: bytes,
    owner: bytes,
    data: bytes,
    path: Optional[str] = None,
) -> None:
    
    p = resolve_path(path)

    if not os.path.exists(p):
        init_file(p)

    prev_hash = _zero32()
    for hdr, dat in iter_blocks(p):
        prev_hash = _hash_block(hdr.pack(), dat)

    if len(case_id) != 32 or len(item_id) != 32:
        raise ValueError("case_id and item_id must be exactly 32 bytes")

    if len(creator) > 12 or len(owner) > 12:
        raise ValueError("creator/owner must be <= 12 bytes")

    hdr_new = Header(
        prev_hash=prev_hash,
        timestamp=time.time(),
        case_id=case_id,
        item_id=item_id,
        state=pad_state(state),
        creator=creator + b"\x00" * (12 - len(creator)),
        owner=owner + b"\x00" * (12 - len(owner)),
        data_length=len(data),
    )

    with open(p, "ab") as f:
        f.write(hdr_new.pack())
        f.write(data)


def get_latest_items(path: Optional[str] = None) -> Dict[bytes, Tuple[bytes, bytes, bytes, bytes]]:
    p = resolve_path(path)
    latest: Dict[bytes, Tuple[bytes, bytes, bytes, bytes]] = {}

    if not os.path.exists(p):
        return latest

    for hdr, _data in iter_blocks(p):
        state = hdr.state.rstrip(b"\x00").decode("ascii", errors="replace")

        if state == "INITIAL" and hdr.case_id == b"0" * 32 and hdr.item_id == b"0" * 32:
            continue

        latest[hdr.item_id] = (
            hdr.case_id,
            hdr.state,
            hdr.creator,
            hdr.owner,
        )
    return latest
