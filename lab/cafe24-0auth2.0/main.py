"""
Cafe24 OAuth 2.0 lab.

순서:
  1) ngrok http 8000 으로 외부 URL 발급
  2) Cafe24 Developers 에 Redirect URI 등록
     https://<ngrok>.ngrok-free.app/auth/cafe24/callback
  3) .env 채우고 서버 실행
     uvicorn main:app --host 0.0.0.0 --port 8000 --reload
  4) 브라우저로 http://localhost:8000/ 접속 → 연결하기 클릭
"""
import base64
import os
import secrets
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

MALL_ID = os.environ["CAFE24_MALL_ID"]
CLIENT_ID = os.environ["CAFE24_CLIENT_ID"]
CLIENT_SECRET = os.environ["CAFE24_CLIENT_SECRET"]
REDIRECT_URI = os.environ["CAFE24_REDIRECT_URI"]
SCOPE = os.environ.get("CAFE24_SCOPE", "mall.read_order")
API_VERSION = os.environ.get("CAFE24_API_VERSION", "2024-09-01")

AUTHORIZE_URL = f"https://{MALL_ID}.cafe24api.com/api/v2/oauth/authorize"
TOKEN_URL = f"https://{MALL_ID}.cafe24api.com/api/v2/oauth/token"
ORDERS_URL = f"https://{MALL_ID}.cafe24api.com/api/v2/admin/orders"

app = FastAPI()

state_store: set[str] = set()
token_store: dict = {}


@app.get("/", response_class=HTMLResponse)
def index():
    has_token = bool(token_store.get("access_token"))
    return f"""
    <h1>Cafe24 OAuth lab</h1>
    <p>access_token 보유: <b>{has_token}</b></p>
    <ol>
      <li><a href="/auth/cafe24/start">Cafe24 연결하기</a></li>
      <li><a href="/test/orders">주문 조회 테스트</a></li>
      <li><a href="/debug/token">현재 토큰 확인</a></li>
    </ol>
    """


@app.get("/auth/cafe24/start")
def start():
    state = secrets.token_urlsafe(16)
    state_store.add(state)
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": state,
    }
    return RedirectResponse(f"{AUTHORIZE_URL}?{urlencode(params)}")


@app.get("/auth/cafe24/callback")
async def callback(
    code: str = Query(...),
    state: str = Query(...),
    error: str | None = Query(None),
    error_description: str | None = Query(None),
):
    if error:
        raise HTTPException(400, f"{error}: {error_description}")
    if state not in state_store:
        raise HTTPException(400, "invalid state")
    state_store.discard(state)

    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            TOKEN_URL,
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )

    if resp.status_code != 200:
        return JSONResponse(
            {"step": "token_exchange", "status": resp.status_code, "body": resp.text},
            status_code=resp.status_code,
        )

    token_store.clear()
    token_store.update(resp.json())
    return JSONResponse({"ok": True, "token": resp.json()})


@app.get("/test/orders")
async def test_orders(
    start_date: str = Query("2017-01-01"),
    end_date: str = Query("2017-12-31"),
):
    access_token = token_store.get("access_token")
    if not access_token:
        raise HTTPException(400, "no access_token. /auth/cafe24/start 먼저 실행")

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            ORDERS_URL,
            params={"start_date": start_date, "end_date": end_date},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "X-Cafe24-Api-Version": API_VERSION,
            },
        )

    ctype = resp.headers.get("content-type", "")
    body = resp.json() if ctype.startswith("application/json") else resp.text
    return JSONResponse({"status": resp.status_code, "body": body})


@app.get("/debug/token")
def debug_token():
    return token_store or {"empty": True}
