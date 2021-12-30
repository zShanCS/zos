from fastapi import FastAPI
from filesystem import FileSystem
app = FastAPI()
fs = FileSystem()

@app.get("/mkdir")
def read_root(command:str):
    x = fs.mkdir(command)
    return {"output": x}

