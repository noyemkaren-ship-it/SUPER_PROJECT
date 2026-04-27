# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.base import get_db, init_db
from services.oll_services import UserService, OrderService
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
import jwt
from routers.routers import router
from routers.test_password import java_chek
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/routers")
print("JAVA CHECK:", java_chek("123456"))


app = FastAPI(title="Tiger Market")

app.include_router(router)

SECRET_KEY = "tiger-secret-key-2024"

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

templates = Jinja2Templates(directory="templates")

def get_user_from_cookie(request: Request):
    token = request.cookies.get("tiger_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_name"]
    except:
        return None

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    user_name = get_user_from_cookie(request)
    if not user_name:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": None
        })
    
    service = UserService(db)
    balance = service.get_balance(user_name)
    orders = OrderService(db).get_user_orders(user_name)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": {
            "name": user_name,
            "balance": balance,
            "orders": [{"quantity": o.quantity, "total_price": o.total_price} for o in orders]
        }
    })

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/catalog")
def catalog_page(request: Request):
    return templates.TemplateResponse("catalog.html", {"request": request})

@app.get("/orders")
def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})

@app.get("/admin")
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})