# routers/all_routers.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database.base import get_db
from services.oll_services import UserService, ItemService, OrderService
from slowapi import Limiter
from slowapi.util import get_remote_address
import hashlib
import jwt
import datetime

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
SECRET_KEY = "tiger-secret-key-2024"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_name: str) -> str:
    return jwt.encode(
        {"user_name": user_name, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        SECRET_KEY, algorithm="HS256"
    )

def set_token_cookie(response, token):
    response.set_cookie("tiger_token", token, httponly=True, max_age=86400, samesite="lax")

@router.post("/users/register")
@limiter.limit("5/minute")
def register(request: Request, name: str, password: str, age: int, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.register(name, hash_password(password), age)
    if not user:
        raise HTTPException(400, "Пользователь уже существует")
    token = create_token(user.name)
    response = JSONResponse({"ok": True, "user": user.name})
    set_token_cookie(response, token)
    return response

@router.post("/users/login")
@limiter.limit("5/minute")
def login(request: Request, name: str, password: str, db: Session = Depends(get_db)):
    service = UserService(db)
    user = service.login(name, hash_password(password))
    if not user:
        raise HTTPException(401, "Неверные данные")
    token = create_token(user.name)
    response = JSONResponse({"ok": True, "user": user.name})
    set_token_cookie(response, token)
    return response

@router.post("/users/logout")
def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie("tiger_token")
    return response

@router.get("/users/balance")
def balance(request: Request, db: Session = Depends(get_db)):
    return {"balance": UserService(db).get_balance(request.state.user)}

@router.post("/items/add")
@limiter.limit("10/minute")
def add_item(request: Request, name: str, price: float, category: str, db: Session = Depends(get_db)):
    item = ItemService(db).add_item(name, request.state.user, price, category)
    return {"id": item.id, "name": item.name, "price": item.price}

@router.get("/items/all")
def all_items(db: Session = Depends(get_db)):
    items = ItemService(db).get_all_items()
    return [{"id": i.id, "name": i.name, "salesman_name": i.salesman_name, "price": i.price, "category": i.category} for i in items]

@router.get("/items/category/{category}")
def items_by_category(category: str, db: Session = Depends(get_db)):
    items = ItemService(db).get_by_category(category)
    return [{"id": i.id, "name": i.name, "price": i.price} for i in items]

@router.post("/orders/create")
@limiter.limit("5/minute")
def create_order(request: Request, quantity: int, salesman_name: str, price: float, db: Session = Depends(get_db)):
    try:
        order = OrderService(db).create_order(request.state.user, quantity, salesman_name, price)
        return {"id": order.id, "total_price": order.total_price}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/orders/user/{user_name}")
def get_user_orders(user_name: str, db: Session = Depends(get_db)):
    orders = OrderService(db).get_user_orders(user_name)
    return [{"id": o.id, "quantity": o.quantity, "total_price": o.total_price} for o in orders]