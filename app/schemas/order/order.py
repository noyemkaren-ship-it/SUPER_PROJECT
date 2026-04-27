from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_name: str
    quantity: int
    salesman_name: str
    price: int

class OrderResponse(BaseModel):
    id: int
    user_name: str
    quantity: int
    salesman_name: str
    price: int
    total_price: int