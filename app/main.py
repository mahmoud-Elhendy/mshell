import sys


def main() -> None:
    term: bool = False
    builtin_commands: set[str] = {"echo","exit","type"}
    while not term:
        sys.stdout.write("$ ")
        # Wait for user input
        command: str = input()
        if command == "exit 0":
            term = True
        elif command.split(' ',1)[0] == "echo":
            print(command.split(' ',1)[1])
        elif command.split(' ',1)[0] == "type":
            param: str = command.split(' ',1)[1]
            if  param in builtin_commands:
                print(f"{param} is a shell builtin")
            else:
                print(f"{param}: not found")

        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
