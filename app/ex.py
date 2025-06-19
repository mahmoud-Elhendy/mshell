import subprocess

# Start `tail -f file.txt`
tail = subprocess.Popen(
    ['tail', '-f', 'file.txt'],
    stdout=subprocess.PIPE,
    text=True
)

# Pipe `tail`'s stdout into `head -n 5`
head = subprocess.Popen(
    ['head', '-n', '5'],
    stdin=tail.stdout,
    stdout=subprocess.PIPE,
    text=True
)

# Allow `tail` to get SIGPIPE if `head` exits
tail.stdout.close()

# Read output from `head` (will block until 5 lines are read)
output, _ = head.communicate()

# Kill tail if it's still running
tail.terminate()
tail.wait()

# Print the output from head
print(output)
