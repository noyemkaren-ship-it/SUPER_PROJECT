# middleware.py
from fastapi import Request
from fastapi.responses import JSONResponse
import jwt

SECRET_KEY = "tiger-secret-key-2024"

async def auth_middleware(request: Request, call_next):
    if request.url.path in ["/", "/register", "/login", "/docs", "/openapi.json", "/favicon.ico"]:
        return await call_next(request)
    token = request.cookies.get("tiger_token")
    if not token:
        return JSONResponse({"error": "Нет доступа"}, 401)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        request.state.user = payload["user_name"]
    except:
        return JSONResponse({"error": "Токен недействителен"}, 401)
    return await call_next(request)