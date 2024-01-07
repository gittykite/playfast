from dotenv import load_dotenv
from pydantic import BaseModel
import httpx
import os 

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# load environment variables
load_dotenv()
API_URL = 'https://api.iamport.kr'
API_KEY = os.environ.get('IMP_API_KEY')
API_SECRET = os.environ.get('IMP_SECRET_KEY')

# load server
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# classes for form validation
class PayResult(BaseModel):
    imp_uid: str
    merchant_uid: str


async def get_imp_token():
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        , 'Accept': 'application/json'
    }
    params = {
        'imp_key': API_KEY
        , 'imp_secret': API_SECRET
    }

    # call IMP API - get access token
    async with httpx.AsyncClient() as client:
        res = await client.post(url=f'{API_URL}/users/getToken', headers=headers, data=params)
        print(res.url)
        print(res.json())

    # raise 401 error when auth fails    
    if res.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    token = res.json()['response']['access_token']
    return token


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

@app.post("/payrecord")
async def pay_record(result: PayResult):
    print('PayResult: ', result)

    token = await get_imp_token()
    headers = {
        'Accept': 'application/json'
        , 'Authorization': f'Bearer {token}'
    }

    # call IMP API - get a single payment record
    async with httpx.AsyncClient() as client:
        res = await client.get(url=f'{API_URL}/payments/{result.imp_uid}', headers=headers)
        print(res.url)
        print(res.json())

    return res.json()


