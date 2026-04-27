# routers/routers.py
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
import httpx
from models.order_models import Order
from models.item_models import Item

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
SECRET_KEY = "tiger-secret-key-2024"

GO_SERVER = "http://localhost:3333"
CPP_SERVER = "http://localhost:4444"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_name: str) -> str:
    return jwt.encode(
        {"user_name": user_name, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        SECRET_KEY, algorithm="HS256"
    )

def set_token_cookie(response, token):
    response.set_cookie("tiger_token", token, httponly=True, max_age=86400, samesite="lax")

def get_current_user(request: Request):
    token = request.cookies.get("tiger_token")
    if not token:
        raise HTTPException(401, "Нет токена в куках")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_name"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Токен истёк")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Токен недействителен")

# ========== ПОЛЬЗОВАТЕЛИ ==========
@router.post("/users/register", tags=["Пользователи"])
@limiter.limit("5/minute")
def register(request: Request, name: str, password: str, age: int, db: Session = Depends(get_db)):
    if not name or not password or not age:
        raise HTTPException(400, "Все поля обязательны")
    if len(name) < 3:
        raise HTTPException(400, "Имя должно быть от 3 символов")
    if len(password) < 6:
        raise HTTPException(400, "Пароль должен быть от 6 символов")
    if age < 10 or age > 120:
        raise HTTPException(400, "Некорректный возраст")
    service = UserService(db)
    if service.get_by_name(name):
        raise HTTPException(400, "Пользователь уже существует")
    user = service.register(name, hash_password(password), age)
    if not user:
        raise HTTPException(500, "Ошибка создания")
    token = create_token(user.name)
    response = JSONResponse({"ok": True, "user": user.name})
    set_token_cookie(response, token)
    return response

@router.post("/users/login", tags=["Пользователи"])
@limiter.limit("5/minute")
def login(request: Request, name: str, password: str, db: Session = Depends(get_db)):
    if not name or not password:
        raise HTTPException(400, "Имя и пароль обязательны")
    service = UserService(db)
    user = service.login(name, hash_password(password))
    if not user:
        raise HTTPException(401, "Неверные данные")
    token = create_token(user.name)
    response = JSONResponse({"ok": True, "user": user.name})
    set_token_cookie(response, token)
    return response

@router.post("/users/logout", tags=["Пользователи"])
def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie("tiger_token")
    return response

@router.get("/users/balance", tags=["Пользователи"])
def balance(request: Request, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    return {"balance": UserService(db).get_balance(user_name)}

@router.post("/users/deposit", tags=["Пользователи"])
@limiter.limit("10/minute")
def deposit(request: Request, amount: float, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    if amount <= 0:
        raise HTTPException(400, "Сумма пополнения должна быть положительной")
    if amount > 100000:
        raise HTTPException(400, "Слишком большая сумма. Максимум 100 000 за раз")
    service = UserService(db)
    user = service.update_balance(user_name, amount)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return {"ok": True, "balance": user.balance, "added": amount}

@router.delete("/users/delete", tags=["Пользователи"])
def delete_account(request: Request, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    service = UserService(db)
    user = service.get_by_name(user_name)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    db.delete(user)
    db.commit()
    response = JSONResponse({"ok": True, "message": "Аккаунт удалён"})
    response.delete_cookie("tiger_token")
    return response


@router.post("/items/add", tags=["Товары"])
@limiter.limit("10/minute")
def add_item(request: Request, name: str, price: float, category: str, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    if not name or not category:
        raise HTTPException(400, "Название и категория обязательны")
    if price <= 0:
        raise HTTPException(400, "Цена должна быть положительной")
    item = ItemService(db).add_item(name, user_name, price, category)
    return {"id": item.id, "name": item.name, "price": item.price}

@router.get("/items/all", tags=["Товары"])
def all_items(db: Session = Depends(get_db)):
    items = ItemService(db).get_all_items()
    return [{"id": i.id, "name": i.name, "salesman_name": i.salesman_name, "price": i.price, "category": i.category} for i in items]

@router.get("/items/category/{category}", tags=["Товары"])
def items_by_category(category: str, db: Session = Depends(get_db)):
    items = ItemService(db).get_by_category(category)
    return [{"id": i.id, "name": i.name, "price": i.price} for i in items]

@router.delete("/items/delete/{item_id}", tags=["Товары"])
def delete_item(request: Request, item_id: int, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    service = ItemService(db)
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "Товар не найден")
    if item.salesman_name != user_name:
        raise HTTPException(403, "Это не ваш товар")
    db.delete(item)
    db.commit()
    return {"ok": True, "message": "Товар удалён"}


@router.post("/orders/create", tags=["Заказы"])
@limiter.limit("5/minute")
def create_order(request: Request, quantity: int, salesman_name: str, price: float, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    if quantity <= 0:
        raise HTTPException(400, "Количество должно быть больше 0")
    if price <= 0:
        raise HTTPException(400, "Цена должна быть положительной")
    if salesman_name == user_name:
        raise HTTPException(400, "Нельзя купить у самого себя")
    try:
        order = UserService(db).create_order(user_name, quantity, salesman_name, price)
        return {"id": order.id, "total_price": order.total_price}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/orders/user/{user_name}", tags=["Заказы"])
def get_user_orders(user_name: str, db: Session = Depends(get_db)):
    orders = OrderService(db).get_user_orders(user_name)
    return [{"id": o.id, "quantity": o.quantity, "total_price": o.total_price} for o in orders]

@router.get("/orders/all", tags=["Заказы"])
def get_my_orders(request: Request, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    orders = OrderService(db).get_user_orders(user_name)
    return [{"id": o.id, "quantity": o.quantity, "salesman_name": o.salesman_name, "price": o.price, "total_price": o.total_price} for o in orders]


@router.get("/go/items", tags=["Go-микросервис"])
def go_items():
    try:
        resp = httpx.get(f"{GO_SERVER}/items")
        return resp.json()
    except:
        raise HTTPException(503, "Go-сервер недоступен")

@router.get("/go/items/{category}", tags=["Go-микросервис"])
def go_items_by_category(category: str):
    try:
        resp = httpx.get(f"{GO_SERVER}/items/{category}")
        return resp.json()
    except:
        raise HTTPException(503, "Go-сервер недоступен")

@router.post("/go/orders", tags=["Go-микросервис"])
def go_create_order(request: Request, quantity: int, salesman_name: str, price: float):
    user_name = get_current_user(request)
    try:
        resp = httpx.post(f"{GO_SERVER}/orders", json={
            "user_name": user_name,
            "quantity": quantity,
            "salesman_name": salesman_name,
            "price": price
        })
        return resp.json()
    except:
        raise HTTPException(503, "Go-сервер недоступен")

@router.get("/cpp/wheel", tags=["C++-микросервис"])
def cpp_wheel():
    try:
        resp = httpx.get(f"{CPP_SERVER}/wheel")
        return resp.json()
    except:
        raise HTTPException(503, "C++ сервер недоступен")
    

@router.delete("/orders/delete/{order_id}", tags=["Заказы"])
def delete_order(request: Request, order_id: int, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    service = OrderService(db)
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заказ не найден")
    if order.user_name != user_name:
        raise HTTPException(403, "Это не ваш заказ")
    db.delete(order)
    db.commit()
    return {"ok": True, "message": f"Заказ #{order_id} удалён"}


@router.get("/admin/orders", tags=["Админ-панель"])
def admin_get_orders(request: Request, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    if user_name != "admin":
        raise HTTPException(403, "Доступ запрещён")
    orders = db.query(Order).all()
    return [{"id": o.id, "user_name": o.user_name, "quantity": o.quantity, "salesman_name": o.salesman_name, "price": o.price, "total_price": o.total_price} for o in orders]

@router.post("/admin/orders/complete/{order_id}", tags=["Админ-панель"])
def admin_complete_order(request: Request, order_id: int, db: Session = Depends(get_db)):
    user_name = get_current_user(request)
    if user_name != "admin":
        raise HTTPException(403, "Доступ запрещён")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Заказ не найден")
    
    # Начисляем админу сумму заказа
    admin = UserService(db).get_by_name("admin")
    if admin:
        admin.balance = (admin.balance or 0) + order.total_price
        db.commit()
        db.refresh(admin)
    
    earned = order.total_price
    db.delete(order)
    db.commit()
    
    return {"ok": True, "message": f"Заказ #{order_id} выполнен", "earned": earned}