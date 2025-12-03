# bchoc/commands/checkout_cmd.py
from datetime import datetime, timezone

from bchoc.env import require_owner_password
from bchoc.ids import item_id_to_enc32, enc32_to_case_uuid
from bchoc.storage import get_latest_items, append_block

TERMINAL_STATES = {"DISPOSED", "DESTROYED", "RELEASED"}

def run_checkout(args) -> int:
    # 1) Check password (any owner-level password)
    require_owner_password(args.password)

    # 2) Parse item id
    try:
        item_id_int = int(args.item_id)
    except ValueError:
        print("> Item ID must be an integer")
        return 1

    item_enc = item_id_to_enc32(item_id_int)

    # 3) Get latest state for this item
    latest = get_latest_items()
    if item_enc not in latest:
        print(f"> Item {item_id_int} not found in blockchain.")
        return 1

    case_enc, state_bytes, creator_bytes, _owner_bytes = latest[item_enc]
    state = state_bytes.rstrip(b"\x00").decode("ascii", errors="replace")

    if state in TERMINAL_STATES:
        print(f"> Item {item_id_int} is in terminal state {state}; cannot checkout.")
        return 1

    if state != "CHECKEDIN":
        print(f"> Item {item_id_int} must be CHECKEDIN to checkout (current: {state}).")
        return 1

    # 4) New owner (up to 12 bytes, padding handled in storage)
    owner_bytes = args.owner.encode("ascii")[:12]

    # 5) Append new CHECKEDOUT block
    append_block(
        case_id=case_enc,
        item_id=item_enc,
        state="CHECKEDOUT",
        creator=creator_bytes.rstrip(b"\x00"),
        owner=owner_bytes,
        data=b"",
    )

    # Prepare time string for output (UTC, ISO 8601 with Z)
    action_time = (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )

    case_str = enc32_to_case_uuid(case_enc)

    print(f"> Case: {case_str}")
    print(f"> Checked out item: {item_id_int}")
    print("> Status: CHECKEDOUT")
    print(f"> Time of action: {action_time}")

    return 0
