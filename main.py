#uvicorn main:app --reload (Executar no terminal)
import locale
import os
from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi import Request
from pydantic import BaseModel
from fastapi import Body
from telethon.sessions import StringSession
from telethon import client
from telethon.types import User
from telethon import TelegramClient
from fastapi.responses import JSONResponse
from telethon.errors import rpcerrorlist
import tracemalloc

app = FastAPI()
templates = Jinja2Templates(directory='templates')
load_dotenv()
sstring = os.getenv("STRING_SESSION")
apiid = os.getenv("API_ID")
apihash = os.getenv("API_HASH")
tphone = None
code = None
pwd = None
code_hash = None
client = TelegramClient(StringSession(sstring), apiid, apihash)

#Class
class tgapi(BaseModel):
    apiID: str
    apiHASH: str

class num1(BaseModel):
    telphon: int

class codex(BaseModel):
    codef: int

class pwd(BaseModel):
    password: str
        
@app.get("/")
async def default():
    global sstring, apiid, apihash, client
    
    if sstring and apiid and apihash:
        print('ok')
    else:
        return RedirectResponse("/signup")
    await client.connect()
    if await client.is_authorized():
        return RedirectResponse("/home")
    else:
        await client.disconnect()
        return RedirectResponse("/signup")

@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request}
    )

@app.get("/signup")
async def signup(request: Request):
    global sstring, apiid, apihash

    if sstring and apiid and apihash:
        return RedirectResponse("/home")
    else:
        return templates.TemplateResponse(
            "signup.html", {'request': request}
        )

@app.post("/api/signup/tglogin/number")
async def tglogin(payload: num1):
    global tphone, code_hash, client
    tphone = payload.telphon
    await client.connect()
    request = await client.send_code_request(tphone)
    code_hash = request.phone_code_hash

@app.post("/api/signup/tglogin/code")
async def codex(payload: codex):
    global tphone, code, code_hash, client
    code = payload.codef
    try:
        await client.sign_in(tphone, code, phone_code_hash=code_hash)
        sessionstr = client.session.save()
        with open('.env', 'a') as f:
            f.write('\nSTRING_SESSION={}'.format(sessionstr))
        return RedirectResponse('/home')

    except rpcerrorlist.SessionPasswordNeededError:
        return JSONResponse(content={'status':'password_needed'})
        
    except rpcerrorlist.PhoneCodeInvalidError:
        code = None
        return JSONResponse(content={'status':'wrong_code'})
    
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return JSONResponse(content={'error': str(e)})

@app.post("/api/signup/tglogin/pwd")
async def pwd(payload: pwd):
    global tphone, code, pwd, client
    pwd = payload.password

    try:
        await client.sign_in(password=pwd)
        sessionstr = client.session.save()
        with open('.env', 'a') as f:
            f.write('\nSESSION_STRING={}'.format(sessionstr))
        return RedirectResponse('/home')

    except rpcerrorlist.PasswordHashInvalidError:
        pwd = None
        return JSONResponse({'status':'wrong_pwd'})
