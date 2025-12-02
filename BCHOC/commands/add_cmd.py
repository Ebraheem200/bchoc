# bchoc/commands/add_cmd.py
"""
Implements: bchoc add
Add one or more items to a case with state CHECKEDIN.
"""

import uuid
from bchoc.env import get_role_for_password
from bchoc.ids import case_uuid_to_enc32, item_id_to_enc32
from bchoc.storage import append_block, iter_blocks

def _existing_items_enc() -> set[bytes]:
    """Collect all encrypted item_ids already in the chain."""
    seen: set[bytes] = set()
    for hdr, _data in iter_blocks():
        seen.add(hdr.item_id)
    return seen

def run_add(args) -> int:
    # 1) Password must be CREATOR
    role = get_role_for_password(args.password)
    if role != "CREATOR":
        print("> Invalid password")
        return 1

    # 2) Validate case UUID
    try:
        uuid.UUID(args.case_id)
    except Exception:
        print("> Invalid case ID (must be a UUID)")
        return 1

    # 3) Convert IDs
    case_enc = case_uuid_to_enc32(args.case_id)
    try:
        item_ids_int = [int(x) for x in args.item_ids]
    except ValueError:
        print("> Item IDs must be integers")
        return 1

    # 4) Check duplicates
    existing = _existing_items_enc()
    for item_id in item_ids_int:
        enc_item = item_id_to_enc32(item_id)
        if enc_item in existing:
            print(f"> Item {item_id} already exists")
            return 1

    # 5) Append one CHECKEDIN block per item
    creator_bytes = args.creator.encode("ascii")[:12]
    owner_bytes = b"\x00" * 12  # initially no separate owner
    for item_id in item_ids_int:
        enc_item = item_id_to_enc32(item_id)
        append_block(
            case_id=case_enc,
            item_id=enc_item,
            state="CHECKEDIN",
            creator=creator_bytes,
            owner=owner_bytes,
            data=b"",
        )
        print(f"> Added item: {item_id}")
        print("> Status: CHECKEDIN")

    return 0
