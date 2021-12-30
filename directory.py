import os
from pathlib import Path

from util import SEP


class Directory:
    def __init__(self, name, working_dir=None):
        '''
        name: the name of the directory
        working_dir: the parent directory path
        '''
        # working_dir => relative path
        if working_dir:
            self.name = name
            self.path = os.path.join(working_dir, name)
        # no working_dir => absolute path
        else:
            self.path = name
            base_name = Path(name).name
            if base_name or base_name == 'c:':
                self.name = name
            else:
                # name is root directory
                self.name = SEP

    def get_path(self):
        return self.path

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, directory):
        return isinstance(directory, Directory) and \
            self.path == directory.get_path()
