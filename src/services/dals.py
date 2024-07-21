from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Account
from src.database.models import Payment
from src.database.models import User
from src.services import hashing


class BaseDAL:
    """
    Базовый класс для всех DAL (Data Access Layer) классов в проекте
    (то есть классов, необходимых для работы с базой данных)
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session: AsyncSession = db_session


class UserDAL(BaseDAL):
    """DAL класс для работы с пользовательскими данными"""

    async def get_user_by_email(self, email: str) -> Optional[User]:
        async with self.db_session.begin():
            result = await self.db_session.execute(select(User).filter_by(email=email))
            return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(User).filter_by(user_id=user_id)
            )
            return result.scalars().first()

    async def delete_user(self, user: User) -> None:
        async with self.db_session.begin():
            await self.db_session.delete(user)

    async def create_user(self, full_name: str, email: str, password: str) -> User:
        async with self.db_session.begin():
            user = User(full_name=full_name, email=email, hashed_password=password)
            self.db_session.add(user)
            await self.db_session.flush(user)

            return user

    async def update_user(
        self, user: User, parameters_for_update: Dict[str, str]
    ) -> None:
        async with self.db_session.begin():
            if (full_name := parameters_for_update.get("full_name", None)) is not None:
                setattr(user, "full_name", full_name)
            if (email := parameters_for_update.get("email", None)) is not None:
                setattr(user, "email", email)
            if (password := parameters_for_update.get("password1", None)) is not None:
                setattr(user, hashing.get_password_hash("hashed_password"), password)

    async def get_users(self) -> List[User]:
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(User).filter_by(is_admin=False)
            )
            return result.scalars().all()


class AccountDAL(BaseDAL):
    """DAL класс для доступа к данным о счетах пользователя"""

    async def get_accounts_by_user_id(self, user_id: int) -> List[Account]:
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(Account).filter_by(user_id=user_id)
            )
            return result.scalars().all()

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(Account).filter_by(account_id=account_id)
            )
            return result.scalars().first()

    async def create_account(self, account_id: int, user_id: int) -> Account:
        async with self.db_session.begin():
            account: Account = Account(user_id=user_id, account_id=account_id)
            self.db_session.add(account)
            await self.db_session.flush()

            return account

    async def change_balance(self, account: Account, amount: float) -> None:
        async with self.db_session.begin():
            setattr(account, "balance", account.balance + amount)


class PaymentDAL(BaseDAL):
    """DAL класс для доступа к данным о платежах"""

    async def get_payment(self, transaction_id: UUID) -> Optional[Payment]:
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(Payment).filter_by(transaction_id=transaction_id)
            )
            return result.scalars().first()

    async def add_payment_to_database(
        self,
        transaction_id: UUID,
        user_id: int,
        account_id: int,
        amount: float,
        signature: str,
    ) -> None:
        async with self.db_session.begin():
            payment: Payment = Payment(
                transaction_id=transaction_id,
                user_id=user_id,
                account_id=account_id,
                amount=amount,
                signature=signature,
            )
            self.db_session.add(payment)
            await self.db_session.flush()

    async def get_payments_by_account_id(
        self, account_id: int
    ) -> Optional[List[Payment]]:
        async with self.db_session.begin():
            result = await self.db_session.execute(
                select(Payment).filter_by(account_id=account_id)
            )
            return result.scalars().all()
