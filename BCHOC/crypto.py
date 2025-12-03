# bchoc/crypto.py
from Crypto.Cipher import AES
from .env import AES_KEY

def _require_len(buf: bytes, n: int, label: str) -> None:
    if len(buf) != n:
        raise ValueError(f"{label} must be exactly {n} bytes (got {len(buf)})")

def encrypt32(plain32: bytes) -> bytes:
    _require_len(plain32, 32, "plain32")
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.encrypt(plain32)

def decrypt32(enc32: bytes) -> bytes:
    _require_len(enc32, 32, "enc32")
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.decrypt(enc32)
