from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    salesman_name: str
    price: int
    category: str

class ItemResponse(BaseModel):
    id: int
    name: str
    salesman_name: str
    price: int
    category: str
