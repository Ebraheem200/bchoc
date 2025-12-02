from bchoc.cli import dispatch
import sys

def main():
    try:
        rc = dispatch()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    sys.exit(rc or 0)

if __name__ == "__main__":
    main()
