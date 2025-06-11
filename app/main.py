import sys


def main() -> None:
    sys.stdout.write("$ ")
    # Wait for user input
    command: str = input()
    print(f"{command}: command not found")


if __name__ == "__main__":
    main()
