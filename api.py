from fastapi import FastAPI
from filesystem import FileSystem
app = FastAPI()
fs = FileSystem()

@app.get("/mkdir")
def makedir(command:str):
    x = fs.mkdir(command)
    return {"output": x}


@app.get("/print")
def print():
    x = fs.print()
    return x

@app.get("/showmm")
def showmm():
    x = fs.show_mm()
    return x


@app.get("/createFile")
def createFile(name:str):
    x = fs.create(name)
    return x
