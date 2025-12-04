# bchoc/commands/show_cmd.py
from argparse import _SubParsersAction, ArgumentParser

from .show_cases_cmd import run_show_cases
from .show_items_cmd import run_show_items
from .show_history_cmd import run_show_history


def add_show_subparsers(show_parser: ArgumentParser) -> None:
    show_sub = show_parser.add_subparsers(dest="show_what", required=True)

    # ---------------- show cases ----------------
    sp_show_cases = show_sub.add_parser("cases", help="List all cases")
    sp_show_cases.add_argument(
        "-p",
        "--password",
        required=False,
        help="Password (shows decrypted case IDs if valid)",
    )
    sp_show_cases.set_defaults(func=run_show_cases)

    # ---------------- show items ----------------
    sp_show_items = show_sub.add_parser("items", help="List items in a case")
    sp_show_items.add_argument(
        "-c",
        "--case_id",
        required=True,
        help="Case UUID",
    )
    sp_show_items.add_argument(
        "-p",
        "--password",
        required=False,
        help="Password (shows decrypted IDs if valid)",
    )
    sp_show_items.set_defaults(func=run_show_items)

    # ---------------- show history --------------
    sp_show_hist = show_sub.add_parser("history", help="Show history of blocks")
    sp_show_hist.add_argument(
        "-c",
        "--case_id",
        required=False,
        help="Case UUID filter",
    )
    sp_show_hist.add_argument(
        "-i",
        "--item_id",
        required=False,
        help="Item ID filter (integer)",
    )
    sp_show_hist.add_argument(
        "-n",
        "--num_entries",
        type=int,
        required=False,
        help="Limit to N entries",
    )
    sp_show_hist.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Show newest entries first",
    )
    sp_show_hist.add_argument(
        "-p",
        "--password",
        required=False,
        help="Password (shows decrypted IDs if valid)",
    )
    sp_show_hist.set_defaults(func=run_show_history)

def run_show(args) -> int:
    # If argparse already set args.func, just call it:
    if hasattr(args, "func"):
        return args.func(args)

    # Fallback: manual dispatch based on show_what
    sub = getattr(args, "show_what", None)
    if sub == "cases":
        return run_show_cases(args)
    if sub == "items":
        return run_show_items(args)
    if sub == "history":
        return run_show_history(args)

    print("> Unknown show subcommand")
    return 1
