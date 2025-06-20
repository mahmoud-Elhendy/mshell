import subprocess
import os
import shlex
import readline
from typing import IO, Union

builtin_commands: set[str] = {"echo", "exit", "type", "pwd", "cd", "history"}
all_commnds: set[str] = builtin_commands.copy()
first_tab: bool = True
paths: list[str] = os.environ['PATH'].split(
    ':') if 'PATH' in os.environ else []
histfile: str | None = os.environ['HISTFILE'] if 'HISTFILE' in os.environ else None
history_list: list[tuple[str, str]] = []
hist_entry_number: int = 1
hist_last_append_idx: int = 0


def echo(parmaters: list[str]) -> tuple[str, str]:
    out: str = ' '.join(parmaters) + "\n"
    return out, ''


def type_cmd(parmaters: list[str]) -> tuple[str, str]:
    global paths
    stdout = ''
    stderr = ''
    if len(parmaters) == 0:
        stderr = "type: missing arg\n"
    elif parmaters[0] in builtin_commands:
        stdout = f"{parmaters[0]} is a shell builtin\n"
    elif (path := command_exist(parmaters[0], paths)) is not None:
        stdout = f"{parmaters[0]} is {path}\n"
    else:
        stderr = f"{parmaters[0]}: not found\n"
    return (stdout, stderr)


def pwd(parmaters: list[str]) -> tuple[str, str]:
    return os.getcwd() + '\n', ''


def cd(parmaters: list[str]) -> tuple[str, str]:
    stderr = ''
    if len(parmaters) == 0:
        stderr = "cd: missing arg\n"
    elif os.path.isdir((expanded_path := os.path.expanduser(parmaters[0]))):
        os.chdir(expanded_path)
    else:
        stderr = f"cd: {parmaters[0]}: No such file or directory\n"
    return '', stderr


def history(parmaters: list[str]) -> tuple[str, str]:
    stdout = ''
    stderr = ''
    if not parmaters:
        stdout = read_history()
    elif len(parmaters) >= 2:
        if parmaters[0] == '-r':
            if not load_history((expanded_path := os.path.expanduser(parmaters[1]))):
                stderr = f'history:{expanded_path} No such file or directory\n'
        elif parmaters[0] == '-w':
            write_history(os.path.expanduser(parmaters[1]))
        elif parmaters[0] == '-a':
            if not append_history(expanded_path := os.path.expanduser(parmaters[1])):
                stderr = f'history:{expanded_path} No such file or directory\n'
    elif len(parmaters) == 1 and parmaters[0].isdigit():
        entries: int = int(parmaters[0])
        stdout = read_history(entries)

    return stdout, stderr


BUILTINS = {
    "echo": echo,
    # "exit": None,
    "pwd": pwd,
    "cd": cd,
    "type": type_cmd,
    "history": history
}


def check_partial_completion(commands: list[str]) -> bool:
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


def redirect(output: str | None, redirs: list[str], append: bool = False) -> None:
    mode: str = "w" if append == False else "a"
    for r in redirs:
        with open(r, mode) as f:
            if output is None:
                output = ''
            f.write(output)


def completer(text: str, state: int) -> str | None:
    global first_tab
    matches: list[str] = sorted(
        cmd for cmd in all_commnds if cmd.startswith(text))
    partial_completion: bool = check_partial_completion(matches)
    if len(matches) == 1 and state == 0:
        return matches[state] + ' '
    if len(matches) > 1 and state == 0 and first_tab and not partial_completion:
        print('\a', end='', flush=True)
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


def exec(command: str, piped: bool = False, stdin: Union[IO[str], str, None] = None) -> Union[tuple[str, str], Union[IO[str] | None, str]]:
    stdout: str = ''
    stderr: str = ''
    redirections: dict[str, list[str]] = {
        '>': [], '1>': [], '2>': [], '>>': [], '1>>': [], '2>>': []}
    parts: list[str] = shlex.split(command)
    if len(parts) == 0:
        return "", ""
    cmd: str = parts[0]
    params: list[str] = list()
    paramters_set = False
    # check redirections
    for i, token in enumerate(parts[1:]):
        if token in redirections and len(parts) > i+1:
            redirections[token].append(parts[1:][i+1])
            paramters_set = True
        elif not paramters_set:
            params.append(token)

    # Handle builtin
    if cmd in BUILTINS:
        if stdin is not None:
            stdout, stderr = BUILTINS[cmd](params + shlex.split(stdin))
        else:
            stdout, stderr = BUILTINS[cmd](params)
        stdout, stderr = check_redir(
            redirections=redirections, stdout=stdout, stderr=stderr)
        if piped:
            return stdout
        else:
            return stdout, stderr
    # not built in command
    elif command_exist(cmd, paths) is not None:
        if stdin is None or isinstance(stdin, str):
            proc = subprocess.Popen(
                [cmd] + params,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if piped:
                return proc.stdout
            else:
                stdout, stderr = proc.communicate(input=stdin)
                stdout, stderr = check_redir(
                    redirections=redirections, stdout=stdout, stderr=stderr)
                return stdout, stderr
        else:
            proc = subprocess.Popen(
                [cmd] + params,
                stdin=stdin,
                stdout=subprocess.PIPE if piped else None,
                stderr=subprocess.PIPE if piped else None,
                text=True
            )
            if stdin:
                stdin.close()

            if piped:
                return proc.stdout
            else:
                stdout, stderr = proc.communicate()
                stdout, stderr = check_redir(
                    redirections=redirections, stdout=stdout, stderr=stderr)
                return stdout, stderr
    else:
        stderr = f"{cmd}: command not found\n"
        stdout, stderr = check_redir(
            redirections=redirections, stdout="", stderr=stderr)
        return stdout, stderr


def check_redir(redirections: dict[str, list[str]], stdout: str | None, stderr: str | None) -> tuple[str, str]:
    stdout_redir: list[str] = redirections['>'] + redirections['1>']
    stdout_append: list[str] = redirections['>>'] + redirections['1>>']
    out = ''
    err = ''
    if stdout_append or stdout_redir:
        if stdout_append:
            redirect(stdout, stdout_append, append=True)
        if stdout_redir:
            redirect(stdout, stdout_redir)
    elif stdout:
        out = stdout

    stderr_redir: list[str] = redirections['2>']
    stderr_append: list[str] = redirections['2>>']
    if stderr_append or stderr_redir:
        if stderr_append:
            redirect(stderr, stderr_append, append=True)
        if stderr_redir:
            redirect(stderr, stderr_redir)
    elif stderr:
        err = stderr
    return out, err


def add_history(command: str) -> None:
    global history_list
    global hist_entry_number
    history_entry: tuple[str, str] = (str(hist_entry_number), command)
    hist_entry_number += 1
    history_list .append(history_entry)


def read_history(entries: int | None = None) -> str:
    global history_list
    if entries == 0:
        return ''
    if entries and entries > 0:
        return ''.join(f'{t[0]} {t[1]}' for t in history_list[-entries:])
    else:
        return ''.join(f'{t[0]} {t[1]}' for t in history_list)


def load_history(path: str) -> bool:
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    add_history(line)
        return True
    else:
        return False


def write_history(path: str) -> None:
    global history_list

    with open(path, 'w') as f:
        for cmd in [t[1] for t in history_list]:
            f.write(cmd)


def append_history(path: str) -> bool:
    global history_list
    global hist_last_append_idx
    if os.path.exists(path):
        if (last_append_list := history_list[hist_last_append_idx:]):
            with open(path, 'a') as f:
                for cmd in [t[1] for t in last_append_list]:
                    f.write(cmd)
            hist_last_append_idx = len(history_list)
        return True
    else:
        return False


def main() -> None:
    global all_commnds
    global histfile
    global paths
    all_commnds |= list_file_names(paths)
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    term: bool = False
    if histfile:
        load_history(histfile)
    while not term:
        # sys.stdout.write("$ ")
        # Wait for user input
        command: str = input("$ ")
        add_history(command + '\n')
        if command == "exit 0":
            if histfile:
                write_history(histfile)
            break
        commands: list[str] = command.split('|')
        stdin = None
        for i, cmd in enumerate(commands):
            if i == (len(commands) - 1):
                res: tuple[str, str] | IO[str] | None | str = exec(
                    command=cmd, piped=False, stdin=stdin)
                if isinstance(res, tuple):
                    if res[0]:
                        print(res[0], end='')
                    if res[1]:
                        print(res[1], end='')
            elif i == 0:
                stdin = exec(cmd, piped=True)
            else:
                stdin = exec(cmd, piped=True, stdin=stdin)


if __name__ == "__main__":
    main()
