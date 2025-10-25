# bchoc

Package: bchoc/

init.py
Marks this directory as a Python package.

main.py
Program entry point for bchoc. Builds the parser and dispatches to commands.

cli.py
Argparse setup. Defines subcommands and routes to bchoc/commands/*.

models.py
Binary header layout (HEADER_FMT), item states, and the Header dataclass. Also includes a helper to pad state to 12 bytes.

crypto.py
AES-ECB helpers for 32-byte fields (case ID and item ID). Replace the placeholder key with the assignment key bytes.

ids.py
Converts external IDs to 32-byte raw buffers before encryption and back again (UUID string ↔ 32 bytes, item int ↔ 32 bytes).

env.py
Reads BCHOC_FILE_PATH and the five role passwords from environment variables.

storage.py
Low-level, append-only binary I/O: create/verify genesis, pack/unpack headers, iterate blocks, append blocks, scan items, item state, per-case summaries, and ID decrypt helpers for display.

verify.py
Full-chain verification: checks SHA-256 links between blocks, file structure, and the per-item state machine (add → CHECKEDIN, alternate CHECKEDIN/CHECKEDOUT, terminal states stop future actions).

Commands: bchoc/commands/

init.py
Empty; enables package imports.

init_cmd.py
Implements bchoc init: create the file and write the INITIAL block if missing; otherwise verify the first block.

add_cmd.py
bchoc add: creator-password check, reject duplicate item IDs, append a CHECKEDIN block per item.

checkout_cmd.py
bchoc checkout: any valid role password, item must be CHECKEDIN, append CHECKEDOUT with new owner.

checkin_cmd.py
bchoc checkin: any valid role password, item must be CHECKEDOUT, append CHECKEDIN.

remove_cmd.py
bchoc remove: creator password required, item must be CHECKEDIN, set DISPOSED/DESTROYED/RELEASED and store release owner if needed.

show_cmd.py
bchoc show: list cases, items, or history. Mask IDs unless a valid password is provided; support count and reverse order.

summary_cmd.py
bchoc summary: per-case totals by the latest state of each item.

verify_cmd.py
bchoc verify: run verification and print “ok” or the first error, returning a non-zero exit code on failure.