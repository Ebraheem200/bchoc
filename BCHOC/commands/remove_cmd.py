# bchoc/commands/remove_cmd.py
from datetime import datetime, timezone

from bchoc.env import require_creator_password
from bchoc.ids import item_id_to_enc32, enc32_to_case_uuid
from bchoc.storage import get_latest_items, append_block

TERMINAL_STATES = {"DISPOSED", "DESTROYED", "RELEASED"}

def run_remove(args) -> int:
    # 1) Password must be CREATOR (exits with code 1 if invalid)
    require_creator_password(args.password)

    # 2) Parse item id
    try:
        item_id_int = int(args.item_id)
    except ValueError:
        print("> Item ID must be an integer")
        return 1

    item_enc = item_id_to_enc32(item_id_int)

    # 3) Get latest state
    latest = get_latest_items()
    if item_enc not in latest:
        print(f"> Item {item_id_int} not found in blockchain.")
        return 1

    case_enc, state_bytes, creator_bytes, _owner_bytes = latest[item_enc]
    state = state_bytes.rstrip(b"\x00").decode("ascii", errors="replace")

    if state in TERMINAL_STATES:
        print(f"> Item {item_id_int} is already in terminal state {state}.")
        return 1

    if state != "CHECKEDIN":
        print(f"> Item {item_id_int} must be CHECKEDIN to remove (current: {state}).")
        return 1

    # 4) Validate target state (reason from -y / --why)
    target_state = args.state.upper()
    if target_state not in TERMINAL_STATES:
        print("> Invalid remove state. Use one of: DISPOSED, DESTROYED, RELEASED.")
        return 1

    # 5) Owner for RELEASED, blank otherwise
    if target_state == "RELEASED":
        if not getattr(args, "owner", None):
            print("> Owner is required when state is RELEASED.")
            return 1
        owner_bytes = args.owner.encode("ascii")[:12]
    else:
        owner_bytes = b""

    # 6) Append terminal state block
    append_block(
        case_id=case_enc,
        item_id=item_enc,
        state=target_state,
        creator=creator_bytes.rstrip(b"\x00"),
        owner=owner_bytes,
        data=b"",  # you could store reason/owner text here if desired
    )

    # 7) Output (include case + time for consistency)
    case_str = enc32_to_case_uuid(case_enc)
    action_time = (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )

    print(f"> Case: {case_str}")
    print(f"> Item {item_id_int} marked as {target_state}.")
    if target_state == "RELEASED":
        print(f"> Released to: {args.owner}")
    print(f"> Time of action: {action_time}")

    return 0
