from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
    )

from models.item_models import Item       
from models.user_models import User       
from models.order_models import Order    
def init_db():
    Base.metadata.create_all(bind=engine)