import subprocess
import os
import shlex
import readline
from typing import IO, Union

builtin_commands: set[str] = {"echo","exit","type","pwd","cd"}

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

def echo(parmaters:list[str]) ->tuple[str,str]:
        out: str = ' '.join(parmaters) + "\n"
        return out,''

def type_cmd(parmaters:list[str])->tuple[str,str]:
    stdout = ''
    stderr = ''
    if len(parmaters) == 0 :
        stderr = "type: missing arg"
    elif  parmaters[0] in builtin_commands:
        stdout = f"{parmaters[0]} is a shell builtin"
    elif (path := command_exist(parmaters[0] , paths)) is not None:
        stdout = f"{parmaters[0]} is {path}"
    else:
        stderr = f"{parmaters[0]}: not found"
    return (stdout,stderr)

def pwd(parmaters:list[str])->tuple[str,str]:
    return os.getcwd(),''

def cd(parmaters:list[str])->tuple[str,str]:
    stderr = ''
    if len(parmaters) == 0 :
        stderr = "cd: missing arg"
    elif os.path.isdir((expanded_path:=os.path.expanduser(parmaters[0]))):
        os.chdir(expanded_path)
    else:
        stderr = f"cd: {parmaters[0]}: No such file or directory" 
    return '',stderr
    
BUILTINS = {
    "echo": echo,
    "exit": None,
    "pwd":pwd,
    "cd": cd,
    "type": type_cmd
}
