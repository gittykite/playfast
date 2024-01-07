from dotenv import load_dotenv
from enum import Enum
from typing import List, Optional
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


# define enums
class PayStatus(Enum):
    UNPAID = 'ready' # 미결제
    PAID = 'paid' # 결제완료
    FAILED = 'failed' # 결제실패
    CANCEL = 'cancelled' # 환불취소


# define form validation classes
class PayResult(BaseModel):
    imp_uid: str
    merchant_uid: str


class PayCancel(BaseModel):
    imp_uid: str
    merchant_uid: Optional[str] = None
    amount: Optional[int] = 0
    tax_free: Optional[int] = 0
    vat_amount: Optional[int] = 0
    checksum: Optional[int] = None
    reason: Optional[str] = None
    refund_holder: Optional[str] = None
    refund_bank: Optional[str] = None
    refund_account: Optional[str] = None
    refund_tel: Optional[str] = None
    extra: List[str] = []


async def get_imp_token():
    token = None

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

    # get access token when success
    if res.status_code == 200 and res.json()['code'] == 0:
            token = res.json()['response']['access_token']
    # raise 401 error when auth fails    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=res.json()['message'],
        )

    return token


async def is_paid_record(imp_uid: str):
    is_paid = False

    token = await get_imp_token()
    headers = {
        'Accept': 'application/json'
        , 'Authorization': f'Bearer {token}'
    }

    # call IMP API - get a single payment record
    async with httpx.AsyncClient() as client:
        res = await client.get(url=f'{API_URL}/payments/{imp_uid}', headers=headers)
        print(res.url)
        print(res.json())

    # check status when valid record exsists
    if res.status_code == 200 and res.json()['code'] == 0:
        status = res.json()['response']['status']
        if(status == PayStatus.PAID.value):
            ispaid = True

    return is_paid


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


@app.post("/paycancel")
async def pay_cancel(req_cancel: PayCancel):
    print('PayCancel: ', req_cancel)

    # set default result message
    result = f'해당 거래는 결제완료 상태가 아닙니다. (imp_uid: {req_cancel.imp_uid})'

    # check if the record is paid status
    is_paid = await is_paid_record(req_cancel.imp_uid)
    if (is_paid):
        token = await get_imp_token()
        params = {
            'imp_uid': req_cancel.imp_uid,
            'merchant_uid': req_cancel.merchant_uid,
            'amount': req_cancel.amount,
            'tax_free': req_cancel.tax_free,
            'vat_amount': req_cancel.vat_amount,
            'checksum': req_cancel.checksum,
            'reason': req_cancel.reason,
            'refund_holder': req_cancel.refund_holder,
            'refund_bank': req_cancel.refund_bank,
            'refund_account': req_cancel.refund_account,
            'refund_tel': req_cancel.refund_tel,
            'extra': req_cancel.extra,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
        }

        # call IMP API - get a single payment record
        async with httpx.AsyncClient() as client:
            res = await client.post(url=f'{API_URL}/payments/cancel', headers=headers, data=params)
            print(res.url)
            print(res.json())
            result = res.json()

    return result
