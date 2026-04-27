from sqlalchemy.orm import Session
from models.item_models import Item

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, salesman_name: str, price: float, category: str) -> Item:
        item = Item(name=name, salesman_name=salesman_name, price=price, category=category)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def get_all(self) -> list[Item]:
        return self.db.query(Item).all()

    def get_by_category(self, category: str) -> list[Item]:
        return self.db.query(Item).filter(Item.category == category).all()