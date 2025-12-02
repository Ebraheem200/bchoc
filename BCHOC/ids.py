# bchoc/ids.py
import uuid
from bchoc.crypto import encrypt32, decrypt32

def _pad32(raw: bytes) -> bytes:
    if len(raw) > 32:
        raise ValueError("value longer than 32 bytes")
    return raw + b"\x00" * (32 - len(raw))

def _strip_zeros(raw32: bytes, expected: int) -> bytes:
    if len(raw32) != 32:
        raise ValueError("must be 32 bytes")
    core = raw32.rstrip(b"\x00")
    if len(core) != expected:
        raise ValueError("unexpected length after unpad")
    return core

# -------- case_id: UUID string <-> enc32 --------

def case_uuid_to_enc32(case_id: str) -> bytes:
    """UUID string -> 32B plaintext (16B uuid + zeros) -> AES-ECB enc32."""
    try:
        u = uuid.UUID(case_id)
    except Exception as e:
        raise ValueError(f"Invalid UUID: {case_id}") from e
    plain32 = _pad32(u.bytes)  # 16B uuid + 16 zeros
    return encrypt32(plain32)

def enc32_to_case_uuid(enc32: bytes) -> str:
    """Reverse of case_uuid_to_enc32."""
    plain32 = decrypt32(enc32)
    raw16 = _strip_zeros(plain32, 16)
    return str(uuid.UUID(bytes=raw16))

# -------- item_id: int <-> enc32 --------

def _int_to_4(n: int) -> bytes:
    if not (0 <= n <= 0xFFFFFFFF):
        raise ValueError("item_id must be in 0..2^32-1")
    return n.to_bytes(4, "big", signed=False)

def _4_to_int(b: bytes) -> int:
    if len(b) != 4:
        raise ValueError("need 4 bytes for item_id")
    return int.from_bytes(b, "big", signed=False)

def item_id_to_enc32(item_id: int) -> bytes:
    """int -> 4B big-endian -> pad to 32 -> AES-ECB enc32."""
    raw4 = _int_to_4(item_id)
    plain32 = _pad32(raw4)
    return encrypt32(plain32)

def enc32_to_item_id(enc32: bytes) -> int:
    """Reverse of item_id_to_enc32."""
    plain32 = decrypt32(enc32)
    raw4 = _strip_zeros(plain32, 4)
    return _4_to_int(raw4)
