from typing import Union
from pydantic import BaseModel, field_validator
from datetime import date

from pydantic_core.core_schema import ValidationInfo


class CustomerBase(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    registration_date: Union[date, str]
    total_spend: float
    last_purchase_date: date


class CustomerCreate(CustomerBase):
    customer_id: int | None = None
    first_name: str | None = None
    last_name: str
    email: str
    registration_date: date | None = None
    total_spend: float | None = None
    last_purchase_date: date | None = None

    @field_validator("*", mode="before")
    def validate(cls, value, info: ValidationInfo):
        if value is '':
            return None
        else:
            return value


class Customer(CustomerBase):
    customer_id: int
    first_name: str | None = None
    last_name: str
    email: str
    registration_date: Union[date, str]
    total_spend: float
    last_purchase_date: date | None = None

    class Config:
        orm_mode = True
