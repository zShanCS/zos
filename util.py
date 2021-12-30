import os
# redirect output of printing
from contextlib import redirect_stdout
from pathlib import Path

# file/directory separator for cross-platform usability
SEP = os.path.sep
'''
Global File Table that keeps track of which threads have opened what file and in which mode
Structure:
{
    filename:
    {
        thread_id: mode
    }
}
For every file, only 1 thread can open a file in w mode at one time
'''
global_file_table = dict()


def get_name(path):
    '''get the file's name'''
    if path == SEP:
        return SEP
    p = Path(path)
    return p.name


def get_parent(path):
    '''get the path to parent directory'''
    p = Path(path)
    parent = p.parent.absolute()
    return str(parent)


def print2file(fs, fn):
    '''
    fs -> FileSystem object
    fn -> file name
    '''
    with open(fn, 'a') as f:
        with redirect_stdout(f):
            fs.print()
            print()


def showmm2file(fs, fn):
    '''
    fs -> FileSystem object
    fn -> file name
    '''
    with open(fn, 'a') as f:
        with redirect_stdout(f):
            fs.show_mm()
            print()


def write2file(fn, txt):
    '''write text to file 'fn'''
    with open(fn, 'a') as f:
        with redirect_stdout(f):
            print(txt)


def is_file_open(fname, thread_id, cache):
    if fname not in cache:
        return False
    if fname not in global_file_table:
        return False
    return thread_id in global_file_table[fname]


def can_write_to_file(fname, thread_id):
    '''
    Must always be preceded by is_file_open()
    Otherwise, it can throw a KeyError
    '''
    return global_file_table[fname][thread_id] == 'w'


def can_read_file(fname, thread_id):
    return global_file_table[fname][thread_id] == 'r'


def assert_file_availability(fname, thread_id, cache, outfile, permission):
    # checks if a file is open / exists
    # checks if thread has a permission
    # writes error message in case checks fail
    if not is_file_open(fname, thread_id, cache):
        write2file(outfile, f"{fname} is not open / doesn't exist")
        return False
    if permission == 'r':
        if not can_read_file(fname, thread_id):
            write2file(
                outfile, f"Thread does not have reading permission for {fname}")
            return False
    if permission == 'w':
        if not can_write_to_file(fname, thread_id):
            write2file(
                outfile, f"Thread does not have writing permission for {fname}")
            return False
    return True


def append(content, text):
    '''append text to end of contents'''
    return content + text


def write_at(content, pos, text):
    '''overwrite text at pos'''
    # text before pos
    new_content = content[:pos]
    # add text at pos
    new_content += text
    # old content had text after pos + len(text) --> retain it
    if pos + len(text) < len(content):
        new_content += content[pos+len(text):]
    return new_content


def move(content, start, size, target):
    '''move contents between [start, start + size] to target'''
    if start > len(content):
        print("Start larger than contents")
        return False
    # the text to move
    move_segment = content[start:start + size]
    # add the text that comes before the segment
    new_content = content[:start]
    # add the text that comes after the segment
    # but before the target
    new_content += content[start + size:target]
    # add the segment at target position
    new_content += move_segment
    # add the remaining text
    new_content += content[target+size:]
    return new_content


def truncate(content, size):
    '''trim content to fit the size'''
    return content[:size]
