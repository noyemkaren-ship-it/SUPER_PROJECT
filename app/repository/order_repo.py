from sqlalchemy.orm import Session
from models.order_models import Order

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_name: str, quantity: int, salesman_name: str, price: float) -> Order:
        order = Order(
            user_name=user_name,
            quantity=quantity,
            salesman_name=salesman_name,
            price=price,
            total_price=quantity * price
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_by_user(self, user_name: str) -> list[Order]:
        return self.db.query(Order).filter(Order.user_name == user_name).all()