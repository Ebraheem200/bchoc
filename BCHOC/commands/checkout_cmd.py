# bchoc/commands/checkout_cmd.py
"""
Implements: bchoc checkout
- Any valid role password allowed.
- Item must currently be CHECKEDIN (and not terminal).
- New owner is stored in 'owner' field.
"""

from bchoc.env import get_role_for_password
from bchoc.ids import item_id_to_enc32
from bchoc.storage import get_latest_items, append_block

TERMINAL_STATES = {"DISPOSED", "DESTROYED", "RELEASED"}


def run_checkout(args) -> int:
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

    # 4) New owner
    owner_bytes = args.owner.encode("ascii")[:12]

    # 5) Append new CHECKEDOUT block
    append_block(
        case_id=case_enc,
        item_id=item_enc,
        state="CHECKEDOUT",
        creator=creator_bytes.rstrip(b"\x00"),  # keep original creator
        owner=owner_bytes,
        data=b"",
    )

    print(f"> Checked out item: {item_id_int}")
    print(f"> New owner: {args.owner}")
    print("> Status: CHECKEDOUT")
    return 0
