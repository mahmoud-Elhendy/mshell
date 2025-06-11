import sys


def main() -> None:
    term: bool = False
    while not term:
        sys.stdout.write("$ ")
        # Wait for user input
        command: str = input()
        if command == "exit 0":
            term = True
        elif command.split(' ',1)[0] == "echo":
            print(command.split(' ',1)[1])
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
