# bchoc/env.py
import os
from typing import Literal, Optional

Role = Literal["POLICE", "LAWYER", "ANALYST", "EXECUTIVE", "CREATOR"]

_ENV_KEYS = {
    "POLICE":    "BCHOC_PASSWORD_POLICE",
    "LAWYER":    "BCHOC_PASSWORD_LAWYER",
    "ANALYST":   "BCHOC_PASSWORD_ANALYST",
    "EXECUTIVE": "BCHOC_PASSWORD_EXECUTIVE",
    "CREATOR":   "BCHOC_PASSWORD_CREATOR",
}

def get_role_for_password(pw: str) -> Optional[Role]:
    """Return the role that matches this password, or None."""
    for role, env_name in _ENV_KEYS.items():
        if os.getenv(env_name) == pw:
            return role  # type: ignore[return-value]
    return None
