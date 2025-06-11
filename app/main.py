import subprocess
import sys
import os

def command_exist(command: str, dirs: list[str]) -> str | None:
    if command == '':
        return None
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
    paths: list[str] = os.environ['PATH'].split(':')
    while not term:
        sys.stdout.write("$ ")
        # Wait for user input
        command: str = input()
        parts: list[str] = command.split(' ', 1)
        if len(parts) == 2:
            prog, parmaters = parts
        else:
            prog= parts[0]
            parmaters: str = ''
        if command == "exit 0":
            term = True
        elif prog == "echo":
            print(parmaters)
        elif prog == "type":
            if  parmaters in builtin_commands:
                print(f"{parmaters} is a shell builtin")
            elif (path := command_exist(parmaters , paths)) is not None:
                print(f"{parmaters} is {path}")
            else:
                print(f"{parmaters}: not found")
        elif (path := command_exist(prog , paths)) is not None:
            tokens: list[str] = [path] + parmaters.split() 
            result: subprocess.CompletedProcess[str] = subprocess.run(tokens, capture_output=True, text=True)
            print(result.stdout)
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
