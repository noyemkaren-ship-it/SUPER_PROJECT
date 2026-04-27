from sqlalchemy.orm import Session
from models.user_models import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, password: str, age: int) -> User:
        user = User(name=name, password=password, age=age, balance=0.0)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_name(self, name: str) -> User | None:
        return self.db.query(User).filter(User.name == name).first()

    def get_all(self) -> list[User]:
        return self.db.query(User).all()

    def update_balance(self, name: str, amount: int) -> User | None:
        user = self.get_by_name(name)
        if user:
            user.balance += amount
            self.db.commit()
            self.db.refresh(user)
        return user