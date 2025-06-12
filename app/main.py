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

def is_quoted(s: str) -> bool:
    return (len(s) >= 2) and ((s[0] == s[-1]) and s[0] in {"'", '"'})

def main() -> None:
    term: bool = False
    builtin_commands: set[str] = {"echo","exit","type","pwd","cd","cat"}
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
            text = ' '.join(shlex.split(parmaters))
            print(text)
        elif prog == "type":
            if  parmaters in builtin_commands:
                print(f"{parmaters} is a shell builtin")
            elif (path := command_exist(parmaters , paths)) is not None:
                print(f"{parmaters} is {path}")
            else:
                print(f"{parmaters}: not found")
        elif prog == "pwd":
            print(os.getcwd())
        elif prog == "cd":
            expanded_path: str = os.path.expanduser(parmaters)
            if os.path.isdir(expanded_path):
                os.chdir(expanded_path)
            else:
                print(f"cd: {parmaters}: No such file or directory")   
        elif prog == "cat":
            for param in shlex.split(parmaters):
                with open(os.path.expanduser(param) , "r") as f:
                    print(f.read(),end='')
            print('')        
        elif command_exist(prog , paths) is not None:
            tokens: list[str] = [prog] + parmaters.split() 
            result: subprocess.CompletedProcess[str] = subprocess.run(tokens, capture_output=True, text=True)
            print(result.stdout.strip())
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
