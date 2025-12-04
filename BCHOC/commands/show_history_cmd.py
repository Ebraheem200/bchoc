# bchoc/commands/show_history_cmd.py
import uuid
from datetime import datetime, timezone
from typing import List, Tuple, Optional

from bchoc.env import get_role_for_password
from bchoc.ids import (
    case_uuid_to_enc32,
    item_id_to_enc32,
    enc32_to_case_uuid,
    enc32_to_item_id,
)
from bchoc.storage import iter_blocks

def _utc_iso(ts: float) -> str:
    """Convert timestamp float (seconds since epoch) to UTC ISO string with Z."""
    return (
        datetime.fromtimestamp(ts, tz=timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )

def run_show_history(args) -> int:
    # 1) Determine privilege from password
    has_priv = False
    if getattr(args, "password", None) is not None:
        role = get_role_for_password(args.password)
        if role is None:
            print("> Invalid password")
            return 1
        has_priv = True

    # 2) Optional case filter
    case_enc_filter: Optional[bytes] = None
    if getattr(args, "case_id", None):
        try:
            uuid.UUID(args.case_id)
        except Exception:
            print("> Invalid case ID (must be a UUID)")
            return 1
        case_enc_filter = case_uuid_to_enc32(args.case_id)

    # 3) Optional item filter
    item_enc_filter: Optional[bytes] = None
    if getattr(args, "item_id", None):
        try:
            item_id_int = int(args.item_id)
        except ValueError:
            print("> Item ID must be an integer")
            return 1
        item_enc_filter = item_id_to_enc32(item_id_int)

    # 4) Collect all matching entries in file order (oldest first)
    entries: List[Tuple] = []
    for hdr, _data in iter_blocks():
        state = hdr.state.rstrip(b"\x00").decode("ascii", errors="replace")
        # skip genesis
        if state == "INITIAL" and hdr.case_id == b"0" * 32 and hdr.item_id == b"0" * 32:
            continue

        if case_enc_filter is not None and hdr.case_id != case_enc_filter:
            continue
        if item_enc_filter is not None and hdr.item_id != item_enc_filter:
            continue

        entries.append((hdr, state))

    if not entries:
        print("> No history entries match the given filters.")
        return 0

    # 5) Apply reverse and num_entries (-n) options
    if getattr(args, "reverse", False):
        entries.reverse()

    if getattr(args, "num_entries", None) is not None:
        n = args.num_entries
        if n < len(entries):
            entries = entries[:n]

    # 6) Print each entry
    for hdr, state in entries:
        if has_priv:
            try:
                case_str = enc32_to_case_uuid(hdr.case_id)
            except Exception:
                case_str = hdr.case_id.hex()
            try:
                item_str = str(enc32_to_item_id(hdr.item_id))
            except Exception:
                item_str = hdr.item_id.hex()
        else:
            case_str = hdr.case_id.hex()
            item_str = hdr.item_id.hex()

        print(f"> Case: {case_str}")
        print(f"> Item: {item_str}")
        print(f"> Action: {state}")
        print(f"> Time: {_utc_iso(hdr.timestamp)}")
        print()

    return 0
