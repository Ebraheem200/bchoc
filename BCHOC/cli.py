import argparse
from bchoc.commands.init_cmd import run_init
from bchoc.commands.add_cmd import run_add
from bchoc.commands.show_cmd import run_show_items
from bchoc.commands.checkout_cmd import run_checkout
from bchoc.commands.checkin_cmd import run_checkin
from bchoc.commands.remove_cmd import run_remove




def build_parser():
    parser = argparse.ArgumentParser(prog="bchoc", description="Blockchain Chain of Custody")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp_init = sub.add_parser("init", help="Initialize blockchain file")
    sp_init.set_defaults(func=lambda args: run_init())
        # bchoc add
    sp_add = sub.add_parser("add", help="Add evidence items to a case")
    sp_add.add_argument("-c", "--case_id", required=True)
    sp_add.add_argument("-i", "--item_ids", required=True, nargs="+")
    sp_add.add_argument("-g", "--creator", required=True)
    sp_add.add_argument("-p", "--password", required=True)
    sp_add.set_defaults(func=run_add)
        # bchoc show-items (debug helper)
    sp_show_items = sub.add_parser("show-items", help="Show latest state for each item (debug)")
    sp_show_items.set_defaults(func=lambda args: run_show_items(args))
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
    sp_remove = sub.add_parser("remove", help="Mark an item as DISPOSED/DESTROYED/RELEASED")
    sp_remove.add_argument("-i", "--item_id", required=True)
    sp_remove.add_argument(
        "-s", "--state",
        required=True,
        help="Terminal state: DISPOSED, DESTROYED, or RELEASED",
    )
    sp_remove.add_argument(
        "-o", "--owner",
        required=False,
        help="Receiver name (required when state is RELEASED)",
    )
    sp_remove.add_argument("-p", "--password", required=True)
    sp_remove.set_defaults(func=run_remove)


    return parser

def dispatch(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
