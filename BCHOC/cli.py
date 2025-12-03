import argparse

from bchoc.commands.init_cmd import run_init
from bchoc.commands.add_cmd import run_add
from bchoc.commands.checkout_cmd import run_checkout
from bchoc.commands.checkin_cmd import run_checkin
from bchoc.commands.remove_cmd import run_remove
from bchoc.commands.summary_cmd import run_summary
from bchoc.commands.verify_cmd import run_verify

from bchoc.commands.show_cases_cmd import run_show_cases
from bchoc.commands.show_items_cmd import run_show_items
from bchoc.commands.show_history_cmd import run_show_history

def build_parser():
    parser = argparse.ArgumentParser(
        prog="bchoc",
        description="Blockchain Chain of Custody",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # bchoc init
    sp_init = sub.add_parser("init", help="Initialize blockchain file")
    sp_init.set_defaults(func=lambda args: run_init())

    # bchoc add
    sp_add = sub.add_parser("add", help="Add evidence items to a case")
    sp_add.add_argument("-c", "--case_id", required=True)
    sp_add.add_argument("-i", "--item_ids", required=True, nargs="+")
    sp_add.add_argument("-g", "--creator", required=True)
    sp_add.add_argument("-p", "--password", required=True)
    sp_add.set_defaults(func=run_add)

    # bchoc checkout
    sp_checkout = sub.add_parser("checkout", help="Check out an item to a new owner")
    sp_checkout.add_argument("-i", "--item_id", required=True)
    sp_checkout.add_argument("-o", "--owner", required=True, help="New owner name")
    sp_checkout.add_argument("-p", "--password", required=True)
    sp_checkout.set_defaults(func=run_checkout)

    # bchoc checkin
    sp_checkin = sub.add_parser("checkin", help="Check in an item")
    sp_checkin.add_argument("-i", "--item_id", required=True)
    sp_checkin.add_argument("-p", "--password", required=True)
    sp_checkin.set_defaults(func=run_checkin)

    # bchoc remove
    sp_remove = sub.add_parser(
        "remove",
        help="Mark an item as DISPOSED/DESTROYED/RELEASED",
    )
    sp_remove.add_argument("-i", "--item_id", required=True)
    sp_remove.add_argument(
        "-s",
        "--state",
        required=True,
        help="Terminal state: DISPOSED, DESTROYED, or RELEASED",
    )
    sp_remove.add_argument(
        "-o",
        "--owner",
        required=False,
        help="Receiver name (required when state is RELEASED)",
    )
    sp_remove.add_argument("-p", "--password", required=True)
    sp_remove.set_defaults(func=run_remove)

    # bchoc show cases/items/history
    sp_show = sub.add_parser("show", help="Show cases, items, or history")
    show_sub = sp_show.add_subparsers(dest="show_what", required=True)
    
    sp_show_cases = show_sub.add_parser("cases", help="List all cases")
    sp_show_cases.add_argument(
        "-p",
        "--password",
        required=False,
        help="Password (shows decrypted case IDs if valid)",
    )
    sp_show_cases.set_defaults(func=run_show_cases)

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

    # bchoc summary -c CASE_ID
    sp_summary = sub.add_parser("summary", help="Summarize item states for a case")
    sp_summary.add_argument(
        "-c",
        "--case_id",
        required=True,
        help="Case UUID",
    )
    sp_summary.set_defaults(func=run_summary)

    # bchoc verify
    sp_verify = sub.add_parser("verify", help="Verify blockchain integrity")
    sp_verify.set_defaults(func=run_verify)

    return parser

def dispatch(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
