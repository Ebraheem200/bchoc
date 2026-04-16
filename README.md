# BCHOC

BCHOC is a Python command-line blockchain-style chain of custody system for digital evidence tracking. It stores evidence records in an append-only binary file and verifies the integrity of the chain using SHA-256 hashes, encrypted identifiers, and strict evidence state transitions.

The project simulates how evidence is added, checked out, checked in, removed, summarized, and verified in a secure chain-of-custody workflow.

---

## Features

- Command-line interface built with `argparse`
- Append-only binary file storage
- SHA-256 hash linking between blocks
- AES encryption helpers for case IDs and item IDs
- Role-based password validation through environment variables
- Evidence state tracking using a strict state machine
- Full blockchain verification for hash links, file structure, and item history
- Commands for initializing, adding, checking out, checking in, removing, showing, summarizing, and verifying evidence records

---

## Project Structure

```text
bchoc/
├── __init__.py
├── main.py
├── cli.py
├── models.py
├── crypto.py
├── ids.py
├── env.py
├── storage.py
├── verify.py
└── commands/
    ├── __init__.py
    ├── init_cmd.py
    ├── add_cmd.py
    ├── checkout_cmd.py
    ├── checkin_cmd.py
    ├── remove_cmd.py
    ├── show_cmd.py
    ├── summary_cmd.py
    └── verify_cmd.py
