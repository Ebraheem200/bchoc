# bchoc/models.py
import struct
from dataclasses import dataclass
from typing import Tuple

# ---------------------------------------------------------------------------
# Binary layout: header format
#
# 32s  : prev_hash (32 bytes)
# d    : timestamp (8-byte double, UTC)
# 32s  : case_id_enc (32 bytes, usually AES-ECB ciphertext-as-raw)
# 32s  : item_id_enc (32 bytes, usually AES-ECB ciphertext-as-raw)
# 12s  : state (ASCII, null-padded to 12 bytes)
# 12s  : creator (ASCII, null-padded to 12 bytes)
# 12s  : owner (ASCII, null-padded to 12 bytes)
# I    : d_length (4-byte unsigned int; length of data that follows)
# ---------------------------------------------------------------------------

HEADER_FMT = "32s d 32s 32s 12s 12s 12s I"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

def pad_state(name: str) -> bytes:
    raw = name.encode("ascii")
    if len(raw) > 12:
        raise ValueError(f"state name '{name}' longer than 12 bytes")
    return raw + b"\x00" * (12 - len(raw))

# State constants (12-byte padded)
STATE_INITIAL   = pad_state("INITIAL")
STATE_CHECKEDIN = pad_state("CHECKEDIN")
STATE_CHECKEDOUT= pad_state("CHECKEDOUT")
STATE_DISPOSED  = pad_state("DISPOSED")
STATE_DESTROYED = pad_state("DESTROYED")
STATE_RELEASED  = pad_state("RELEASED")

def state_to_str(state: bytes) -> str:
    return state.rstrip(b"\x00").decode("ascii", errors="ignore")

# Header and Block dataclasses
@dataclass
class Header:
    prev_hash: bytes
    timestamp: float
    case_id_enc: bytes
    item_id_enc: bytes
    state: bytes
    creator: bytes
    owner: bytes
    d_length: int

    def pack(self) -> bytes:
        """Pack the header into binary using HEADER_FMT."""
        return struct.pack(
            HEADER_FMT,
            self.prev_hash,
            self.timestamp,
            self.case_id_enc,
            self.item_id_enc,
            self.state,
            self.creator,
            self.owner,
            self.d_length,
        )

    @classmethod
    def unpack_from(cls, buf: bytes, offset: int) -> Tuple["Header", int]:
        chunk = buf[offset:offset + HEADER_SIZE]
        fields = struct.unpack(HEADER_FMT, chunk)
        header = cls(*fields)
        return header, offset + HEADER_SIZE

@dataclass
class Block:
    header: Header
    data: bytes

    def pack(self) -> bytes:
        self.header.d_length = len(self.data)
        return self.header.pack() + self.data

    @classmethod
    def unpack_from(cls, buf: bytes, offset: int) -> Tuple["Block", int]:
        header, after_header = Header.unpack_from(buf, offset)
        data_start = after_header
        data_end = data_start + header.d_length
        data = buf[data_start:data_end]
        block = cls(header=header, data=data)
        return block, data_end
