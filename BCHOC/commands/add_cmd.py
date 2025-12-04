# bchoc/commands/add_cmd.py
import uuid
from datetime import datetime, timezone

from bchoc.env import require_creator_password
from bchoc.ids import case_uuid_to_enc32, item_id_to_enc32
from bchoc.storage import append_block, iter_blocks

def _existing_items_enc() -> set[bytes]:
    seen: set[bytes] = set()
    for hdr, _data in iter_blocks():
        seen.add(hdr.item_id)
    return seen

def run_add(args) -> int:
    # 1) Password must be CREATOR (exits with code 1 if invalid)
    require_creator_password(args.password)

    # 2) Validate case UUID
    try:
        uuid.UUID(args.case_id)
    except Exception:
        print("> Invalid case ID (must be a UUID)")
        return 1

    # 3) Convert case_id to encrypted 32-byte field
    case_enc = case_uuid_to_enc32(args.case_id)

    # 4) Parse item IDs as integers
    try:
        item_ids_int = [int(x) for x in args.item_ids]
    except ValueError:
        print("> Item IDs must be integers")
        return 1

    if not item_ids_int:
        print("> No item IDs provided")
        return 1

    # 5) Check for duplicates against existing chain
    existing = _existing_items_enc()
    for item_id in item_ids_int:
        enc_item = item_id_to_enc32(item_id)
        if enc_item in existing:
            print(f"> Item {item_id} already exists")
            return 1

    # 6) Prepare creator/owner fields (12-byte ASCII, padded in storage)
    creator_bytes = args.creator.encode("ascii")[:12]
    # For simplicity, set owner == creator on add (spec does not constrain this)
    owner_bytes = creator_bytes

    # 7) Append one CHECKEDIN block per item
    action_time = (
        datetime.now(timezone.utc)
        .isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
    )

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
        print(f"> Time of action: {action_time}")

    return 0
