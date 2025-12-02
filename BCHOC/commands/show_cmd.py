# bchoc/commands/show_items_cmd.py
"""
Implements: bchoc show-items
Debug-style listing of latest state for each item.
"""

from bchoc.storage import get_latest_items

def run_show_items(args) -> int:
    items = get_latest_items()

    if not items:
        print("> No items in blockchain.")
        return 0

    print("> Latest state per item:")
    for idx, (item_enc, (case_enc, state_bytes, creator_bytes, owner_bytes)) in enumerate(items.items(), start=1):
        state = state_bytes.rstrip(b"\x00").decode("ascii", errors="replace")
        creator = creator_bytes.rstrip(b"\x00").decode("ascii", errors="replace") or "(none)"
        owner = owner_bytes.rstrip(b"\x00").decode("ascii", errors="replace") or "(none)"

        item_hex = item_enc.hex()
        case_hex = case_enc.hex()

        # shorten hex to keep printout readable
        item_short = f"{item_hex[:8]}…{item_hex[-8:]}"
        case_short = f"{case_hex[:8]}…{case_hex[-8:]}"
        print(f"#{idx}")
        print(f"  Item (enc): {item_short}")
        print(f"  Case (enc): {case_short}")
        print(f"  State    : {state}")
        print(f"  Creator  : {creator}")
        print(f"  Owner    : {owner}")
        print()
    return 0
