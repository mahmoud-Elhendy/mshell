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

def handle_stdout(stdout: str , redirs :list[str]) -> None:
    for r in redirs:
        with open(r,"w") as f:
            f.write(stdout)

def main() -> None:
    term: bool = False
    builtin_commands: set[str] = {"echo","exit","type","pwd","cd"}
    paths: list[str] = os.environ['PATH'].split(':')
    redirections: dict[str,list[str]] = {'>':[], '1>':[] ,'2>':[], '>>':[], '1>>':[], '2>>':[]}
    while not term:
        sys.stdout.write("$ ")
        # Wait for user input
        stdout = str()
        stderr = str()
        command: str = input()
        parts: list[str] = shlex.split(command)
        if len(parts) == 0:
            continue
        prog: str = parts[0]
        parmaters: list[str] = list()
        paramters_set =  False
        #check redirections
        for i,token in enumerate(parts[1:]):
            if token in redirections and  len(parts) > i+1:
                redirections[token].append(parts[1:][i+1])
            elif not paramters_set:
                parmaters.append(token)
                paramters_set = True


        if command == "exit 0":
            term = True
        elif prog == "echo":
            text: str = ' '.join(parmaters)
            stdout = text
        elif prog == "type":
            if len(parmaters) == 0 :
                stderr = "type: missing arg"
            elif  parmaters[0] in builtin_commands:
                stdout = f"{parmaters[0]} is a shell builtin"
            elif (path := command_exist(parmaters[0] , paths)) is not None:
                stdout = f"{parmaters[0]} is {path}"
            else:
                stderr = f"{parmaters[0]}: not found"
        elif prog == "pwd":
            stdout = os.getcwd()
        elif prog == "cd":
            if len(parmaters) == 0 :
                stderr = "cd: missing arg"
            elif os.path.isdir((expanded_path:=os.path.expanduser(parmaters[0]))):
                os.chdir(expanded_path)
            else:
                stderr = f"cd: {parmaters[0]}: No such file or directory"   
        elif command_exist(prog , paths) is not None:
            result: subprocess.CompletedProcess[str] = subprocess.run(parts, capture_output=True, text=True)
            stdout = result.stdout.strip()
        else:
            stderr = f"{command}: command not found"

        #check redir
        stdout_redir: list[str] = redirections['>'] + redirections['1>']
        if len(stdout_redir) > 0:
            handle_stdout(stdout, stdout_redir)
        else:
            print(stdout)


            
if __name__ == "__main__":
    main()
