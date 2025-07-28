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

async def tgconnect():
    global tphone, code, pwd, code_hash, sstring, apiid, apihash
    client = TelegramClient(StringSession(sstring), apiid, apihash)
    if tphone == None:
        return JSONResponse({'message':'number_empty'})
    await client.connect()
    if pwd != None:
        try:
            await client.sign_in(tphone, code, pwd, phone_code_hash=code_hash)
            sessionstr = client.session.save()
            with open('.env', 'w') as f:
                f.write(f"STRING_SESSION={sessionstr}\n")

        except rpcerrorlist.PasswordHashInvalidError:
            return JSONResponse({'status':'wrong_pwd'})
    if code != None:
        try:
            await client.sign_in(tphone, code, phone_code_hash=code_hash)

        except rpcerrorlist.SessionPasswordNeededError:
            print('Need password')
            return JSONResponse(content={'status':'password_needed'})
        
        except rpcerrorlist.PhoneCodeInvalidError:
            print('Wrong code')
            return JSONResponse(content={'status':'wrong_code'})
        
        except Exception as e:
            await client.disconnect()
            print(str(e))
            return JSONResponse(content={'error':'{}'.format(str(e))})

    else:
        request = await client.send_code_request(tphone)
        code_hash = request.phone_code_hash
        
@app.get("/")
async def default():
    global sstring, apiid, apihash
    
    if sstring and apiid and apihash:
        print('ok')
    else:
        return RedirectResponse("/signup")
    
    async with TelegramClient(StringSession(sstring), apiid, apihash) as client:
         if await client.is_user_authorized():
              return RedirectResponse("/home")
         else:
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

@app.post("/api/signup/tgapis")
async def api_signup(payload: tgapi):
        apiID = int(payload.apiID)
        apiHASH = str(payload.apiHASH)
        with open('.env', 'w') as f:
            f.write(f"API_ID={apiID}\n")
            f.write(f"API_HASH={apiHASH}\n")
        return {'status':'ok'}

@app.post("/api/signup/tglogin/number")
async def tglogin(payload: num1):
    global tphone
    tphone = payload.telphon

    await tgconnect()

@app.post("/api/signup/tglogin/code")
async def codex(payload: codex):
    global tphone, code, code_hash
    code = payload.codef

    await tgconnect()

@app.post("/api/signup/tglogin/pwd")
async def pwd(payload: pwd):
    global tphone, code, pwd
    pwd = payload.password

    await tgconnect()