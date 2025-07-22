#uvicorn main:app --reload (Executar no terminal)
import locale
import os
from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi import Request
from pydantic import BaseModel
from telethon.sessions import StringSession


app = FastAPI()
templates = Jinja2Templates(directory='templates')

@app.get("/")
async def default():
    empty=[]
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("API_ID=\n")
            f.write("API_HASH=\n")
            f.write("SESSION_STRING=\n")
    print(os.getenv('API_ID'))
    if not os.getenv("API_ID"):
        empty.append('API_ID')
    if not os.getenv("API_HASH"):
        empty.append('API_HASH')
    if not os.getenv("SESSION_STRING"):
        empty.append('STRING_SESSION')
    if empty:
        return RedirectResponse('/signup')
    else:
        return RedirectResponse('/home')

@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request}
    )

@app.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse(
        "signup.html", {"request": request}
    )

class tgapi(BaseModel):
    apiID: str
    apiHASH: str

@app.post("/api/signup/tgapis")
async def api_signup(apiID: str = Form(...), apiHASH: str = Form(...)):
        with open('.env', 'x') as f:
            f.write(f"API_ID={apiID}\n")
            f.write(f"API_HASH={apiHASH}\n")

class num(BaseModel):
    num: int
    
@app.post("/api/signup/tglogin/number")
async def tglogin(num: int):
    print(num)