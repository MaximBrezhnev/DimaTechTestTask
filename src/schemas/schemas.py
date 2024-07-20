from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict

from src.schemas.mixins import UserValidationMixin


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class ShowUserSchema(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class UserCreationSchema(UserValidationMixin, BaseModel):
    email: EmailStr
    full_name: str
    password1: str
    password2: str


class UserUpdateSchema(UserValidationMixin, BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password1: Optional[str] = None
    password2: Optional[str] = None


class ShowAccountSchema(BaseModel):
    account_id: int
    balance: float


class PaymentSchema(BaseModel):
    transaction_id: UUID
    user_id: int
    account_id: int
    amount: float
    signature: str

