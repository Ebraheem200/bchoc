# bchoc/commands/show_items_cmd.py
import uuid

from bchoc.env import get_role_for_password
from bchoc.ids import case_uuid_to_enc32, enc32_to_item_id
from bchoc.storage import get_latest_items

def run_show_items(args) -> int:
    # 1) Validate case_id (must be UUID)
    try:
        uuid.UUID(args.case_id)
    except Exception:
        print("> Invalid case ID (must be a UUID)")
        return 1

    # Encrypted form used for equality comparison
    case_enc_filter = case_uuid_to_enc32(args.case_id)

    # 2) Determine whether we have a valid owner password
    #    - If password is valid => show decrypted values
    #    - If password is missing or invalid => show encrypted hex
    role = None
    if getattr(args, "password", None) is not None:
        role = get_role_for_password(args.password)
    has_priv = role is not None

    # 3) Get latest items and filter by case_enc
    all_latest = get_latest_items()
    filtered = [
        (item_enc, case_enc, state_bytes, creator_bytes, owner_bytes)
        for item_enc, (case_enc, state_bytes, creator_bytes, owner_bytes)
        in all_latest.items()
        if case_enc == case_enc_filter
    ]

    if not filtered:
        if has_priv:
            print(f"> No items found for case {args.case_id}")
        else:
            print(f"> No items found for case {args.case_id}")
        return 0

    # 4) Print results
    for idx, (item_enc, case_enc, state_bytes, creator_bytes, owner_bytes) in enumerate(filtered, start=1):
        state = state_bytes.rstrip(b"\x00").decode("ascii", errors="replace")
        creator = creator_bytes.rstrip(b"\x00").decode("ascii", errors="replace") or "(none)"
        owner = owner_bytes.rstrip(b"\x00").decode("ascii", errors="replace") or "(none)"

        if has_priv:
            # Decrypted view
            item_str = str(enc32_to_item_id(item_enc))
            case_str = args.case_id
        else:
            # Encrypted/obfuscated view
            item_hex = item_enc.hex()
            case_hex = case_enc.hex()
            item_str = item_hex
            case_str = case_hex

        print(f"> Item #{idx}")
        print(f">   Case : {case_str}")
        print(f">   Item : {item_str}")
        print(f">   State: {state}")
        print(f">   Creator: {creator}")
        print(f">   Owner  : {owner}")
        print()

    return 0
