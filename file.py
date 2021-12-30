import os
import sys


class File:
    def __init__(self, name, working_dir=None):
        '''
        name: the name of the file
        working_dir: the parent directory path
        '''
        # relative path
        if working_dir:
            self.name = name
            self.path = os.path.join(working_dir, name)
        # absolute path
        else:
            self.path = name
            self.name = os.path.basename(name)
        # contents of the file
        self.contents = ''
        # file size in bytes
        self.adjust_size()
        # the pages that this file is occupying
        self.occupied_pages = []

    def __str__(self):
        return self.name

    def get_path(self):
        return self.path

    def set_path(self, path):
        dirname = os.path.dirname(path)
        fname = os.path.basename(path)
        # path contains filename too
        if fname:
            self.path = os.path.join(dirname, fname)
            self.set_name(fname)
        # keep original name; just change directory
        else:
            self.path = os.path.join(dirname, self.name)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_contents(self):
        return self.contents

    def set_contents(self, content):
        self.contents = content
        self.adjust_size()

    def get_pages(self):
        return self.occupied_pages

    def set_pages(self, pages):
        self.occupied_pages = pages

    def get_size(self):
        return self.size

    def adjust_size(self):
        self.size = sys.getsizeof(self.contents)

    def read(self):
        '''read all contents'''
        return self.contents

    def read_from(self, start, size):
        '''read text between start till start + size'''
        if start < len(self.content):
            return self.content[start:start + size]
        else:
            return ''

    def __eval__(self):
        return self.path

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, file):
        return isinstance(file, File) and self.path == file.get_path()
