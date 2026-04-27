
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from database.base import init_db
from routers.routers import user_router, item_router, order_router

app = FastAPI(title="Tiger Market")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

templates = Jinja2Templates(directory="templates")

app.include_router(user_router.router)
app.include_router(item_router.router)
app.include_router(order_router.router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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