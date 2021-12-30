import os
from concurrent.futures import ThreadPoolExecutor

from filesystem import FileSystem
from thread_runner import thread_runner

# files = [
#     "input_thread1.txt",
#     "input_thread2.txt"
# ]

files = []

while True:
    name = input("Enter a filename or 'x' to exit:  ")
    if name == 'x':
        break
    elif os.path.exists(name) and os.path.isfile(name):
        files.append(name)
    else:
        print("File not found.")

fs = FileSystem()
fs_duplicated = [fs] * len(files)
outfiles = [f'output_thread{i+1}.txt' for i in range(len(files))]
# clear contents of file
for outfile in outfiles:
    if os.path.exists(outfile):
        open(outfile, "w").close()
commands_per_file = list()
for input_file in files:
    with open(input_file) as f:
        commands = f.readlines()
        # remove newlines
        commands = [command.strip() for command in commands]
    commands_per_file.append(commands)
args = tuple(zip(range(len(files)), outfiles,
             fs_duplicated, commands_per_file))
with ThreadPoolExecutor(max_workers=len(files)) as executor:
    executor.map(lambda p: thread_runner(*p), args)
