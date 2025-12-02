from bchoc.storage import init_file

def run_init() -> int:
    created, msg = init_file()
    print(f"> {msg}")
    return 0
