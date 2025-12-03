# bchoc/commands/show_cases_cmd.py
from bchoc.env import get_role_for_password
from bchoc.ids import enc32_to_case_uuid
from bchoc.storage import iter_blocks

def run_show_cases(args) -> int:
    # Determine privilege level
    has_priv = False
    if getattr(args, "password", None) is not None:
        role = get_role_for_password(args.password)
        if role is None:
            print("> Invalid password")
            return 1
        has_priv = True

    # Build map: case_enc -> set(item_enc)
    cases: dict[bytes, set[bytes]] = {}

    for hdr, _data in iter_blocks():
        state = hdr.state.rstrip(b"\x00").decode("ascii", errors="replace")
        # Skip genesis block
        if state == "INITIAL" and hdr.case_id == b"0" * 32 and hdr.item_id == b"0" * 32:
            continue

        if hdr.case_id not in cases:
            cases[hdr.case_id] = set()
        cases[hdr.case_id].add(hdr.item_id)

    if not cases:
        print("> No cases in blockchain.")
        return 0

    # Print results
    for idx, (case_enc, items) in enumerate(cases.items(), start=1):
        if has_priv:
            try:
                case_str = enc32_to_case_uuid(case_enc)
            except Exception:
                case_str = case_enc.hex()
        else:
            case_str = case_enc.hex()

        print(f"> Case #{idx}")
        print(f">   Case ID      : {case_str}")
        print(f">   Unique items : {len(items)}")
        print()

    return 0
