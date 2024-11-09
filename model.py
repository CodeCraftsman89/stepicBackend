from pydantic import BaseModel, EmailStr, PositiveInt, Field


class User(BaseModel):
    name: str
    id: int


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: PositiveInt | None = Field(default=None, lt=130)
    is_subscribed: bool = False


class Feedback(BaseModel):
    name: str
    message: str


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
