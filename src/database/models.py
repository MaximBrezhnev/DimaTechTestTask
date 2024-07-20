from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    is_admin: Mapped[bool] = mapped_column(default=False)
    full_name: Mapped[str]
    hashed_password: Mapped[str]
    accounts: Mapped[List["Account"]] = relationship(back_populates="user")


class Account(Base):
    __tablename__ = "account"

    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    balance: Mapped[float] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    user: Mapped["User"] = relationship(back_populates="accounts")
    payments: Mapped[List["Payment"]] = relationship(back_populates="account")


class Payment(Base):
    __tablename__ = "payment"

    payment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[UUID] = mapped_column(unique=True)
    amount: Mapped[float]
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"))
    account: Mapped["Account"] = relationship(back_populates="payments")




