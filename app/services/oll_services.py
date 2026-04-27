from repository.user_repo import UserRepository
from repository.item_repo import ItemRepository
from repository.order_repo import OrderRepository

class UserService:
    def __init__(self, db):
        self.repo = UserRepository(db)

    def register(self, name, password, age):
        if self.repo.get_by_name(name):
            return None
        return self.repo.create(name, password, age)

    def login(self, name, password):
        user = self.repo.get_by_name(name)
        if user and user.password == password:
            return user
        return None

    def get_balance(self, name):
        user = self.repo.get_by_name(name)
        if user:
            return user.balance
        return None

    def update_balance(self, name, amount):
        return self.repo.update_balance(name, amount)


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