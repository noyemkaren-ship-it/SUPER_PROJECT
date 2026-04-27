# services/oll_services.py
from repository.user_repo import UserRepository
from repository.item_repo import ItemRepository
from repository.order_repo import OrderRepository

class UserService:
    def __init__(self, db):
        self.repo = UserRepository(db)
        self.db = db

    def get_by_name(self, name):
        return self.repo.get_by_name(name)

    def register(self, name, password, age):
        return self.repo.create(name, password, age)

    def login(self, name, password):
        user = self.repo.get_by_name(name)
        if user and user.password == password:
            return user
        return None

    def get_balance(self, name):
        user = self.repo.get_by_name(name)
        return user.balance if user and user.balance else 0

    def update_balance(self, name, amount):
        user = self.repo.get_by_name(name)
        if not user:
            return None
        user.balance = (user.balance or 0) + amount
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_order(self, user_name, quantity, salesman_name, price):
        total = quantity * price
        balance = self.get_balance(user_name)
        if balance < total:
            raise Exception(f"Недостаточно средств. Баланс: {balance}₽, нужно: {total}₽")
        self.update_balance(user_name, -total)
        return OrderRepository(self.db).create(user_name, quantity, salesman_name, price)


class ItemService:
    def __init__(self, db):
        self.repo = ItemRepository(db)

    def add_item(self, name, salesman_name, price, category):
        return self.repo.create(name, salesman_name, price, category)

    def get_all_items(self):
        return self.repo.get_all()

    def get_by_category(self, category):
        return self.repo.get_by_category(category)


class OrderService:
    def __init__(self, db):
        self.repo = OrderRepository(db)

    def create_order(self, user_name, quantity, salesman_name, price):
        return self.repo.create(user_name, quantity, salesman_name, price)

    def get_user_orders(self, user_name):
        return self.repo.get_by_user(user_name)