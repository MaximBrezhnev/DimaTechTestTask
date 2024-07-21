from typing import Optional
from uuid import UUID

from fastapi import Form
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field

from src.schemas.mixins import UserValidationMixin


class OAuth2PasswordRequestFormEmail:
    """
    Схема, используемая для входа пользователя в систему

    Атрибуты:
    username (str): Электронная почта пользователя, являющаяся также
    и его username (подобное наименование необходимо для корректной
    работы документации);
    password (str): Пароль пользователя
    """

    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
    ):
        self.email = username
        self.password = password


class TokenSchema(BaseModel):
    """
    Схема для представления access token'а и refresh token'а.

    Атрибуты:
    access_token (str): Токен доступа.
    refresh_token (Optional[str]): Refresh token. Если с помощью схемы происходит обновление токена доступа, то
    refresh token не возвращается, следовательно, поле остается пустым.
    token_type (str): Тип токена, обычно "Bearer".
    """

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str


class ShowUserSchema(BaseModel):
    """
    Схема для отображения информации о пользователе.

    Атрибуты:
    user_id (int): Уникальный идентификатор пользователя;
    full_name (str): Полное имя пользователя;
    email (EmailStr): Электронная почта пользователя
    """

    user_id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class UserCreationSchema(UserValidationMixin, BaseModel):
    """
    Схема для данных, передаваемых при создании пользователя.

    Атрибуты:
    full_name (str): Полное имя пользователя;
    email (EmailStr): Электронная почта пользователя;
    password1 (str): Пароль пользователя;
    password2 (str): Повторение пароля для подтверждения;
    """

    email: EmailStr
    full_name: str
    password1: str
    password2: str


class UserUpdateSchema(UserValidationMixin, BaseModel):
    """
    Схема для данных, передаваемых при обновлении пользователя

    Атрибуты:
    full_name (Optional[str]): Новое полное имя пользователя (необязательно);
    email (Optional[EmailStr]): Новая почта пользователя (необязательно);
    password1 (Optional[str]): Новое пароль пользователя (необязательно);
    password2 (Optional[str]): Подтверждение нового пароля пользователя (необязательно).
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password1: Optional[str] = None
    password2: Optional[str] = None


class ShowAccountSchema(BaseModel):
    """
    Схема для отображения информации о пользовательском счете

    Атрибуты:
    account_id (int): Уникальный идентификатор счета;
    balance (float): Баланс счета.
    """

    account_id: int
    balance: float


class PaymentSchema(BaseModel):
    """
    Схема, представляющая данные платежа

    Атрибуты:
    transaction_id (UUID): Уникальный идентификатор транзакции в “сторонней системе”;
    account_id (int): Уникальный идентификатор счета пользователя, c которым связан платеж;
    amount (float): Сумма пополнения счета пользователя;
    signature (str): Подпись транзакции
    """

    transaction_id: UUID
    user_id: int
    account_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0.0)
    signature: str
