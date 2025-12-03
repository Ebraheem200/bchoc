# bchoc/env.py
import os
from typing import Optional, Literal

Role = Literal["POLICE", "LAWYER", "ANALYST", "EXECUTIVE", "CREATOR"]

_ENV_KEYS = {
    "POLICE":    "BCHOC_PASSWORD_POLICE",
    "LAWYER":    "BCHOC_PASSWORD_LAWYER",
    "ANALYST":   "BCHOC_PASSWORD_ANALYST",
    "EXECUTIVE": "BCHOC_PASSWORD_EXECUTIVE",
    "CREATOR":   "BCHOC_PASSWORD_CREATOR",
}

AES_KEY = b"R0chLi4uLi4uLi4="

BLOCKCHAIN_FILE = os.environ.get("BCHOC_FILE_PATH", "bchoc.dat")

# Load password values
PW_POLICE     = os.getenv("BCHOC_PASSWORD_POLICE")
PW_LAWYER     = os.getenv("BCHOC_PASSWORD_LAWYER")
PW_ANALYST    = os.getenv("BCHOC_PASSWORD_ANALYST")
PW_EXECUTIVE  = os.getenv("BCHOC_PASSWORD_EXECUTIVE")
PW_CREATOR    = os.getenv("BCHOC_PASSWORD_CREATOR")

# Creator-only password
CREATOR_PASSWORD = PW_CREATOR

# Owner-level passwords: (creator counts as owner)
OWNER_PASSWORDS = {
    pw for pw in [
        PW_POLICE,
        PW_LAWYER,
        PW_ANALYST,
        PW_EXECUTIVE,
        PW_CREATOR,
    ]
    if pw is not None
}

def get_role_for_password(pw: str) -> Optional[Role]:
    for role, env_name in _ENV_KEYS.items():
        if os.getenv(env_name) == pw:
            return role
    return None

def require_creator_password(pw: str):
    if pw != CREATOR_PASSWORD:
        print("> Invalid password")
        raise SystemExit(1)

def require_owner_password(pw: str):
    if pw not in OWNER_PASSWORDS:
        print("> Invalid password")
        raise SystemExit(1)
