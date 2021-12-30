# Threaded File System
Logical file system that implements paging, multithreading, etc.

## Usage
Run each cell on [Google Colab](https://colab.research.google.com/drive/1C33cZiobMuFcwgzpCEnobYj0jVThKL7Z?usp=sharing)

**OR**

Run locally: `python main.py`

### Settings
- No. of Pages: 10,000
- Page Size: 64 B

### Notes
1. If a thread opens a file for modification, the changes it makes will not be saved until it closes the file.
2. Reading a file's contents is already thread safe (point 3 touches this further).
3. A thread cannot read the updated contents of a file until the writer thread has closed the file.
4. A file is **locked** for modification by a single thread.

**Additional Features**
- Global File Table that maps that uses filename to index into the threads that have opened the file and the associated file mode.
- Integers are returned by the FileSystem object to indicate failure status.
