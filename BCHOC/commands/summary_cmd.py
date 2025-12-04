# bchoc/commands/summary_cmd.py
import uuid

from bchoc.ids import case_uuid_to_enc32
from bchoc.storage import iter_blocks

TRACKED_STATES = ["CHECKEDIN", "CHECKEDOUT", "DISPOSED", "DESTROYED", "RELEASED"]

def run_summary(args) -> int:
    # 1) Validate case UUID
    try:
        uuid_obj = uuid.UUID(args.case_id)
    except Exception:
        print("> Invalid case ID (must be a UUID)")
        return 1

    # Encrypted version used to match blocks
    case_enc_filter = case_uuid_to_enc32(str(uuid_obj))

    # 2) Iterate blocks and gather stats
    unique_items = set()
    counts = {state: 0 for state in TRACKED_STATES}

    for hdr, _data in iter_blocks():
        if hdr.case_id != case_enc_filter:
            continue

        state_str = hdr.state.rstrip(b"\x00").decode("ascii", errors="replace")
        if state_str == "INITIAL":
            continue

        unique_items.add(hdr.item_id)
        if state_str in counts:
            counts[state_str] += 1

    # 3) Handle case with no blocks
    if not unique_items and all(v == 0 for v in counts.values()):
        print(f"> No records found for case {args.case_id}")
        return 0

    # 4) Print summary
    print(f"> Case: {args.case_id}")
    print(f"> Unique item IDs: {len(unique_items)}")
    for state in TRACKED_STATES:
        print(f"> {state:9}: {counts[state]}")

    return 0
