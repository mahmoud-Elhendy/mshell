import subprocess
import sys
import os
import shlex
import readline

builtin_commands: set[str] = {"echo","exit","type","pwd","cd"}
all_commnds: set[str] = builtin_commands.copy()
first_tab: bool = True

def check_partial_completion(commands: list[str]) ->bool:
    if not commands:
        return False
    common: str = commands[0]
    for command in commands[1:]:
        if not command.startswith(common):
            return False
    return True
    
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

def redirect(output: str| None , redirs :list[str], append: bool = False) -> None:
    mode: str = "w" if append == False else "a"
    for r in redirs:
        with open(r,mode) as f:
            if output is None:
                output = ''
            f.write(output)

def completer(text: str, state: int) -> str | None:
    global first_tab
    matches: list[str] = sorted(cmd for cmd in all_commnds if cmd.startswith(text))
    partial_completion: bool = check_partial_completion(matches)
    if len(matches) == 1 and state == 0:
        return matches[state] + ' ' 
    if len(matches) > 1 and state == 0 and first_tab and not partial_completion:
        print('\a',end='', flush=True)
        first_tab = False
        return None
    if state < len(matches):
        return matches[state]
    else:
        first_tab = True
        return None

def list_file_names(paths: list[str]) -> set[str]:
    file_names: set[str] = set()
    for path in paths:
        if os.path.isdir(path):
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isfile(full_path):
                    file_names.add(entry)
    return file_names

def main() -> None:
    global all_commnds
    paths: list[str] = os.environ['PATH'].split(':')
    all_commnds |= list_file_names(paths)
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    term: bool = False
    
    while not term:
        #sys.stdout.write("$ ")
        # Wait for user input
        stdout: str | None = None
        stderr: str | None = None
        redirections: dict[str,list[str]] = {'>':[], '1>':[] ,'2>':[], '>>':[], '1>>':[], '2>>':[]}
        command: str = input("$ ")
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
                paramters_set = True
            elif not paramters_set:
                parmaters.append(token)
                
        if command == "exit 0":
            term = True
        elif prog == "echo":
            text: str = ' '.join(parmaters) + "\n"
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
            result: subprocess.CompletedProcess[str] = subprocess.run([prog] + parmaters, capture_output=True, text=True)
            if result.stdout:
                stdout = result.stdout
            if result.stderr:
                stderr = result.stderr
        else:
            stderr = f"{command}: command not found"

        #check redir
        stdout_redir: list[str] = redirections['>'] + redirections['1>']
        stdout_append: list[str] = redirections['>>'] + redirections['1>>']
        if stdout_append or stdout_redir:
            if stdout_append:
                redirect(stdout, stdout_append, append=True)
            if stdout_redir:
                redirect(stdout, stdout_redir)
        elif stdout is not None:
            print(stdout.strip())

        stderr_redir: list[str] = redirections['2>']
        stderr_append: list[str] = redirections['2>>']
        if stderr_append or stderr_redir:
            if stderr_append:
                redirect(stderr, stderr_append, append=True)
            if stderr_redir:
                redirect(stderr, stderr_redir)
        elif stderr is not None:
            print(stderr.strip())

if __name__ == "__main__":
    main()
