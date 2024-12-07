from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
class QuestionRequest(BaseModel):
    question:str

# Serve static files (like your HTML file)
app.mount("/static", StaticFiles(directory="D:/New Folder/WEBPAGE/static"), name="static")

# Serve the HTML file at the root
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r") as f:
        content = f.read()
    return content

from googlesearch import search
def web(question):
    l1=[]
    for result in search(question, num_results=3):
        l1.append(result)
    return l1
@app.post("/website")
async def website(question:QuestionRequest):
    return {"response":web(question.question)}