# bchoc/commands/checkin_cmd.py
"""
Implements: bchoc checkin
- Any valid role password allowed.
- Item must currently be CHECKEDOUT (and not terminal).
- On checkin, owner is cleared.
"""

from bchoc.env import get_role_for_password
from bchoc.ids import item_id_to_enc32
from bchoc.storage import get_latest_items, append_block

TERMINAL_STATES = {"DISPOSED", "DESTROYED", "RELEASED"}


def run_checkin(args) -> int:
    # 1) Check password (any valid role)
    role = get_role_for_password(args.password)
    if role is None:
        print("> Invalid password")
        return 1

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
        print(f"> Item {item_id_int} is in terminal state {state}; cannot checkin.")
        return 1

    if state != "CHECKEDOUT":
        print(f"> Item {item_id_int} must be CHECKEDOUT to checkin (current: {state}).")
        return 1

    # 4) On checkin, owner becomes blank
    owner_bytes = b""

    # 5) Append CHECKEDIN block
    append_block(
        case_id=case_enc,
        item_id=item_enc,
        state="CHECKEDIN",
        creator=creator_bytes.rstrip(b"\x00"),
        owner=owner_bytes,
        data=b"",
    )

    print(f"> Checked in item: {item_id_int}")
    print("> Status: CHECKEDIN")
    return 0
