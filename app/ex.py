import subprocess
import shlex
import io
from typing import IO, Union

def echo(input:list[str]) ->tuple[str,str]:
        out: str = ' '.join(input) + "\n"
        return out,''

BUILTINS = {
    "echo": echo
}

def exec(command: str, piped: bool = False, stdin: Union[IO[str],str,None] = None) -> Union[tuple[str,str] , Union[IO[str] | None , str]]:
    tokens = shlex.split(command)

    params: list[str] = tokens[1:]
    cmd: str = tokens[0]
    # Handle builtin
    if cmd in BUILTINS:
        if stdin is not None:
            out = BUILTINS[cmd](shlex.split(stdin))
        else:
            out = BUILTINS[cmd](params)    
            
        if piped:
            return out[0]
        else:
             return out      
    # not built in command    
    else:
        if stdin is not None and isinstance(stdin, str):     
            proc = subprocess.Popen(
                tokens,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if piped:
                 return proc.stdout
            else:
                return proc.communicate(input=stdin)
        else:
             proc = subprocess.Popen(
                tokens,
                stdin=stdin,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
             if piped:
                return proc.stdout
             else:
                return proc.communicate()
             

# echo is builtin, tail and head are external
out1: IO[str] = exec("cat main.py", piped=True)
print(out1)
out2: IO[str] = exec("wc", stdin=out1)

print(out2)