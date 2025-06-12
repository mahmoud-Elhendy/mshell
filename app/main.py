import subprocess
import sys
import os
import shlex

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
    builtin_commands: set[str] = {"echo","exit","type","pwd","cd"}
    paths: list[str] = os.environ['PATH'].split(':')
    while not term:
        sys.stdout.write("$ ")
        # Wait for user input
        command: str = input()
        parts: list[str] = shlex.split(command)
        if len(parts) == 0:
            continue
        prog = parts[0]
        parmaters = list()
        if len(parts) > 1:
            parmaters: list[str] = parts[1:]

        if command == "exit 0":
            term = True
        elif prog == "echo":
            text = ' '.join(parmaters)
            print(text)
        elif prog == "type":
            if len(parmaters) == 0 :
                print("type: missing arg")
            elif  parmaters[0] in builtin_commands:
                print(f"{parmaters[0]} is a shell builtin")
            elif (path := command_exist(parmaters[0] , paths)) is not None:
                print(f"{parmaters[0]} is {path}")
            else:
                print(f"{parmaters[0]}: not found")
        elif prog == "pwd":
            print(os.getcwd())
        elif prog == "cd":
            if len(parmaters) == 0 :
                print("cd: missing arg")
            elif os.path.isdir((expanded_path:=os.path.expanduser(parmaters[0]))):
                os.chdir(expanded_path)
            else:
                print(f"cd: {parmaters[0]}: No such file or directory")   
        elif command_exist(prog , paths) is not None:
            result: subprocess.CompletedProcess[str] = subprocess.run(parts, capture_output=True, text=True)
            print(result.stdout.strip())
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
