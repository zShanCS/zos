import os
import pickle
import sys
from math import ceil
from pathlib import Path

from treelib import Tree

from directory import Directory
from file import File
from util import *


class FileSystem:
    def __init__(self):
        # tree that represents the file system
        self.fs = Tree()
        if os.name == 'nt':
            # root directory
            self.root = Directory("c:")
            # only allow 1 mountable drive (C drive)
            self.fs.create_node("C:", "c:", data=self.root)
        else:
            # posix paths
            # initial directory is root
            self.root = Directory(SEP)
            # arg1: name to display; arg2: internel tag; arg3: contents of node
            self.fs.create_node(SEP, SEP, data=self.root)
        # self.curr_pointer always points to a Directory object
        self.curr_pointer = self.root
        # free frames list; 0 -> free / 1 -> occupied
        self.free_frames = [0] * 10000

    def mkdir(self, dirname):
        '''
        Ignore duplicate directory
        Ignore non-existent parent directory
        '''
        dirname, dirpath, full_path = self._get_components(dirname)
        if self._exists(full_path):
            print("Duplicate directory. Operation ignored.")
            return 0
        if not self._exists(dirpath):
            print("No such parent directory exists!")
            return 1
        directory = Directory(dirname, dirpath)
        self.fs.create_node(dirname, full_path, parent=dirpath, data=directory)
        return full_path

    def cd(self, dirname):
        '''
        Check for path type
        Check if dir exists
        Change pointer
        '''
        _, _, full_path = self._get_components(dirname)
        if self._exists(full_path):
            self.curr_pointer = self.fs.get_node(full_path).data
        else:
            return 0
        return self.pwd()

    def mv(self, src_fname, dst_fname):
        _, _, src_full_path = self._get_components(
            src_fname)
        dst_filename, dst_dirname, dst_full_path = self._get_components(
            dst_fname)
        if not self._exists(src_full_path):
            print("Source file doesn't exist!")
            return 0
        if not self._exists(dst_dirname):
            print("Destination directory doesn't exist!")
            return 1

        # we will overwrite destination file
        # so delete it for now
        if self._exists(dst_full_path):
            self.delete(dst_full_path)

        src_node = self.fs.get_node(src_full_path)
        src_file = src_node.data
        src_file.set_path(dst_full_path)

        self.fs.move_node(src_full_path, dst_dirname)
        self.fs.update_node(src_full_path, tag=dst_filename,
                            identifier=dst_full_path)
        return True

    def pwd(self):
        return self.curr_pointer.get_path()

    def print(self):
        self.fs.show()

    def show_mm(self):
        '''
        Show memory map
        If file occupies > 0 pages then print
        filepath, pages, size
        '''
        for node in self.fs.all_nodes_itr():
            file = node.data
            if isinstance(file, File):
                size = file.get_size()
                pages = file.get_pages()
                if len(pages) > 0:
                    print(file.get_path(), pages, size)

    def save(self, name):
        with open(name, "wb") as outp:
            pickle.dump(self, outp, pickle.HIGHEST_PROTOCOL)

    def create(self, fname):
        '''
        Get filename, directory of parent, and full_path
        Ignore operation if directory of parent does not exist or file already exists
        Create File object and then add to tree
        '''
        filename, dirname, full_path = self._get_components(fname)
        if not self._exists(dirname):
            print("No such directory exists!")
            return 0
        if self._exists(full_path):
            print("Duplicate file. Operation ignored.")
            return 1
        file = File(filename, dirname)
        self.fs.create_node(filename, full_path, parent=dirname, data=file)
        self._allocate_pages(file)
        return full_path

    def delete(self, fname):
        '''
        Check if file doesn't exist
        Otherwise delete it
        '''
        _, _, full_path = self._get_components(fname)
        if not self._exists(full_path):
            print("No such file exists!")
            return False
        self.fs.remove_node(full_path)
        return True

    def open(self, fname):
        _, _, full_path = self._get_components(fname)
        if not self._exists(full_path):
            print("File doesn't exist!")
            return False
        file = self.fs.get_node(full_path).data
        return file

    def close(self, fname, new_contents):
        '''
        If the contents of the file changed, 
        then save the new contents in 'new_contents'
        It is assumed that file hasn't changed if old_contents == new_contents
        Modify the page table/free frame list
        '''
        _, _, full_path = self._get_components(fname)
        if not self._exists(full_path):
            print("File doesn't exist!")
            return 0
        file = self.fs.get_node(full_path).data
        old_contents = file.get_contents()
        if new_contents != old_contents:
            if self._are_frames_available(file, new_contents):
                file.set_contents(new_contents)
                self._allocate_pages(file)
            else:
                print("Not enough frames available to save this change.")
                return 1
        return True

    def _exists(self, path):
        '''
        Provide a path to directory or file
        and check if it exists in this data structure
        '''
        return self.fs.contains(path)

    def _are_frames_available(self, file, content):
        '''check if the new content can be allocated to the file'''
        num_frames_required = ceil(sys.getsizeof(content) / 64)
        num_frames_released = len(file.get_pages())
        # number of 0s -> number of free frames + the number of pages that are released
        num_free_frames = len(self.free_frames) - \
            sum(self.free_frames) + num_frames_released
        return num_free_frames >= num_frames_required

    def _allocate_pages(self, file):
        '''
        file -> File object in tree
        '''
        size = file.get_size()
        pages = file.get_pages()

        # under-allocated file
        while len(pages) < ceil(size / 64):
            # find a free page
            page = self.free_frames.index(0)
            self.free_frames[page] = 1
            pages.append(page)
        # over-allocated file
        if len(pages) > ceil(size / 64):
            required = ceil(size / 64)
            for i, pg_num in enumerate(pages):
                if i > required:
                    self.free_frames[pg_num] = 0
            pages = pages[:required]
        file.set_pages(pages)

    def _get_components(self, path):
        '''
        Pass path and get 3 components
            1. Name of node
            2. Path to node's parent
            3. The absolute node path
        '''
        # special case
        if path == SEP:
            return (SEP,) * 3
        elif path.lower() == "c:" + SEP:
            return ("c:") * 3

        p = Path(path)
        # node name
        name = get_name(path)
        # directory path of parent
        parent_path = str(p.parent)
        # absolute path
        if p.is_absolute():
            full_path = str(p.absolute())
            return (name, parent_path, full_path)
        # relative path
        else:
            # if path to directory, then nodes[-1] might be a '', so remove it
            nodes = path.split('/')
            if nodes[-1] == '':
                nodes = nodes[:-1]
            # current directory
            current_dir = self.curr_pointer.get_path()
            for node in nodes:
                # parent directory
                if node == '..':
                    current_dir = get_parent(current_dir)
                # current directory
                elif node == '.':
                    continue
                else:
                    current_dir = os.path.join(current_dir, node)
            name = Path(current_dir).name
            # exclude the base node
            current_dir = get_parent(current_dir)
            return (name, current_dir, os.path.join(current_dir, name))


if __name__ == '__main__':
    fs = FileSystem()
    fs.create("file1.txt")
    fs.print()
