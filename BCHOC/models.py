import struct
from dataclasses import dataclass

HEADER_FMT = "32s d 32s 32s 12s 12s 12s I"
HEADER_SIZE = struct.calcsize(HEADER_FMT)

def pad_state(name: str) -> bytes:
    raw = name.encode("ascii")
    return raw + b"\x00" * (12 - len(raw))

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
