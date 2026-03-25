from typing import List

from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    active: bool = Field(default=True)
    admin: bool = Field(default=False)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "John",
                "email": "user@example.com",
                "password": "12345",
                "active": True,
                "admin": False,
            }
        },
    }


class OrderSchema(BaseModel):
    user: int

    model_config = {"from_attributes": True}


class LoginSchema(BaseModel):
    email: str
    password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {"email": "user@example.com", "password": "12345"}
        },
    }


class OrderItemSchema(BaseModel):
    quantity: int
    flavor: str
    size: str
    unit_price: float

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "quantity": 1,
                "flavor": "chocolate",
                "size": "medium",
                "unit_price": 5.0,
            }
        },
    }


class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    price: float
    items: List[OrderItemSchema]

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "status": "pending",
                "price": "10.0",
                "items": [
                    {
                        "quantity": 1,
                        "flavor": "chocolate",
                        "size": "medium",
                        "unit_price": 5.0,
                    }
                ],
            }
        },
    }
