#uvicorn main:app --reload (Executar no terminal)
import locale
import os
from fastapi import FastAPI
from fastapi import RedirectResponse

app = FastAPI()
pathenv = ".env"

LANG = 'PT' if locale.getdefaultlocale('pt') else 'EN'

@app.get("/")
async def default():
    if not os.path.exists(pathenv):
        with open(pathenv, 'w') as f:
            f.write('SESSION_STRING=\n')
            f.write('API_ID=\n')
            f.write('API_HASH=\n')
    else:
        return RedirectResponse('/signup')