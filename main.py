import os
import json
import asyncio
import random
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import rpcerrorlist, FloodWaitError
from telethon.tl.functions.channels import CreateChannelRequest

app = FastAPI()
templates = Jinja2Templates(directory='templates')
load_dotenv()
sstring = os.getenv("SESSION_STRING")
apiid = os.getenv("API_ID")
apihash = os.getenv("API_HASH")
tphone = None
code = None
pwd = None
code_hash = None
client = TelegramClient(StringSession(sstring), apiid, apihash)
progress_file = 'progress.json'
class startclone(BaseModel):
    source_id: int | str
    destination_is_new: bool
    destination_id: int | str | None
    
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
        pass
    else:
        return RedirectResponse("/signup")
    await client.connect()
    if await client.is_user_authorized():
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
            f.write('\nSESSION_STRING={}'.format(sessionstr))
        await client.disconnect()
        return RedirectResponse('/home')

    except rpcerrorlist.SessionPasswordNeededError:
        return JSONResponse(content={'status':'password_needed'})
        
    except rpcerrorlist.PhoneCodeInvalidError:
        code = None
        return JSONResponse(content={'status':'wrong_code'})
    
@app.post("/api/signup/tglogin/pwd")
async def pwd(payload: pwd):
    global tphone, code, pwd, client
    pwd = payload.password

    try:
        await client.sign_in(password=pwd)
        sessionstr = client.session.save()
        with open('.env', 'a') as f:
            f.write('\nSESSION_STRING={}'.format(sessionstr))
        await client.disconnect()
        return RedirectResponse('/home')

    except rpcerrorlist.PasswordHashInvalidError:
        pwd = None
        return JSONResponse({'status':'wrong_pwd'})

@app.get('/api/tginfo')
async def getinfo():
    global client
    await client.connect()
    if os.path.exists(progress_file):
        return JSONResponse({'is_cloning_in_progress': True})
    dialogs = await client.get_dialogs()
    channels = sorted(
        [d for d in dialogs
         if d.is_channel], key=lambda x: x.name.lower())
    jchan = [
        {"id":canal.id, "name":canal.name}
        for canal in channels
        ]
    return JSONResponse({'is_cloning_in_progress': False, 'channels': jchan})

@app.post("/api/start")
async def cloning(payload: startclone):
    global client, src, dst
    source = payload.source_id
    new = payload.destination_is_new
    dest = payload.destination_id

    if not new:
        src = source
        dst = dest
    else:
        src = source
        dst = 'create'
    
    asyncio.create_task(main())
    return JSONResponse({'status':'ok'})

@app.get('/cloning')
async def clon(request: Request):
    return templates.TemplateResponse(
        'cloning.html', {'request': request}
    )

@app.get("/api/cloning_status")
async def get_cloning_status():
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
            return JSONResponse(content=data)
        except (json.JSONDecodeError, FileNotFoundError):
            return JSONResponse(content={'status':'error', 'message':'Progress file not found'})
    else:
        return JSONResponse({'status':'completed', 'message':'Cloning process finished'})
    
async def main():
    global client, src, dst, progress_file
    try:
        await client.connect()
        
        if dst == 'create':
            source_entity = await client.get_entity(src)
            result = await client(CreateChannelRequest(
                title=source_entity.title + ' - Clone',
                about="Cloned using https://github.com/DevHuney/tg-cloner",
                megagroup=False))
            dst = str(result.chats[0].id)
            dst = int('-100' + dst)

        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
                last_message_id = progress.get('last_message_id', 0)
        except FileNotFoundError:
            last_message_id = 0
            with open(progress_file, 'w') as f:
                json.dump({'status':'in_progress', 'last_message_id': 0, 'total_cloned': 0}, f)
        
        tosend = []
        cloned_count = 0

        async for message in client.iter_messages(src, reverse=True, offset_id=last_message_id):
            if hasattr(message, 'text') or hasattr(message, 'media'):
                tosend.append(message)
                if len(tosend) >= 10:
                    await send_save(client, tosend, dst)
                    tosend = []

        if tosend:
            await send_save(client, tosend, dst)
        
        try:
            with open(progress_file, 'r') as f:
                final_progress = json.load(f)
                final_count = final_progress.get('cloned', 0)
        except:
            final_count = 0
            
        with open(progress_file, 'w') as f:
            json.dump({'status': 'completed', 'message': f'Successfully cloned {final_count} messages!'}, f)
        
        await asyncio.sleep(3)
        if os.path.exists(progress_file):
            os.remove(progress_file)
        
    except asyncio.CancelledError:
        with open(progress_file, 'w') as f:
            json.dump({'status':'error', 'message':'Cloning process was cancelled'}, f)
    except Exception as e:
        with open(progress_file, 'w') as f:
            json.dump({'status':'error', 'message':str(e)}, f)
    finally:
        try:
            await client.disconnect()
        except:
            pass

async def send_save(client, messages, dst):
    global progress_file

    for message in messages:
        try:
            if hasattr(message, 'media') and message.media:
                await client.send_message(dst, message)
            elif hasattr(message, 'text') and message.text:
                await client.send_message(dst, message)
            else:
                continue
                
            try:
                with open(progress_file, 'r') as f:
                    progress = json.load(f)
                progress['last_message_id'] = message.id
                progress['cloned'] = progress.get('cloned', 0) + 1
                with open(progress_file, 'w') as f:
                    json.dump(progress, f, indent=4)
            except Exception as e:
                pass
            
            delay = random.uniform(1, 5)
            await asyncio.sleep(delay)
                
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
            await client.send_message(dst, message)
        except Exception as e:
            pass