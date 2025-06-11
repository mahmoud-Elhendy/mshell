import sys
import os

def command_exist(command: str, dirs: list[str]) -> str | None:
    for dir in dirs:
        try:
            files: list[str] = os.listdir(dir)
            if command in files:
                return os.path.join(dir, command)
        except FileNotFoundError:
            continue
    return None

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
            paths: list[str] = os.environ['PATH'].split(':')
            print(paths)
            if  param in builtin_commands:
                print(f"{param} is a shell builtin")
            elif (file := command_exist(param , paths)) is not None:
                print(f"{param} is {file}")
            else:
                print(f"{param}: not found")

        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
