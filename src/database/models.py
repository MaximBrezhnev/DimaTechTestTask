from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Модель для представления пользователей в базе данных

    Атрибуты:
    user_id (int): Уникальный идентификатор пользователя, генерируется автоматически
    full_name (str): Полное имя пользователя.
    is_admin (bool): Флаг, указывающий, является ли пользователь администратором
    email (str): Уникальный e-mail пользователя.
    hashed_password (str): Хэшированный пароль пользователя.
    accounts (list[Account]): Отношение, представляющее собой счета, принадлежащие
    данному пользователю
    """

    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    full_name: Mapped[str]
    hashed_password: Mapped[str]
    accounts: Mapped[List["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Account(Base):
    """
    Модель для представления счетов пользователей в базе данных

    Атрибуты:
    account_id (int): Уникальный идентификатор счета, генерируется автоматически
    balance (float): Баланс счета
    user_id (int): Внешний ключ, представляющий собой идентификатор пользователя, которому
    принадлежит счет
    user (User): Отношение, необходимое для возможности обращения к объекту пользователя, обладающего счетом
    payments (list[Payment]): Отношение, представляющее собой список платежей, свяазнынх с текущим счетом
    """

    __tablename__ = "account"

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    balance: Mapped[float] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    user: Mapped["User"] = relationship(back_populates="accounts")
    payments: Mapped[List["Payment"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class Payment(Base):
    """
    Модель для представления платежей в базе данных

    Атрибуты:
    payment_id (int): Уникальный идентификатор платежа в базе данных. Генерируется автоматически
    transaction_id (UUID): Уникальный идентификатор транзакции в “сторонней системе”
    account_id (int): Внешний ключ, представляющий собой уникальный идентификатор счета пользователя
    amount (float): Сумма пополнения счета пользователя
    account (Account): Отношение, представляющее собой объект счета, с которым связан платеж
    signature (str): Подпись транзакции
    """

    __tablename__ = "payment"

    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[UUID] = mapped_column(unique=True)
    amount: Mapped[float]
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"))
    account: Mapped["Account"] = relationship(back_populates="payments")
    signature: Mapped[str]
