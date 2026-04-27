from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    name: str
    password: str
    age: int

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    balance: int

