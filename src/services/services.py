from datetime import timedelta
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Account
from src.database.models import Payment
from src.database.models import User
from src.services import hashing
from src.services import security
from src.services.dals import AccountDAL
from src.services.dals import PaymentDAL
from src.services.dals import UserDAL
from src.settings import project_settings


class BaseService:
    """
    Базовый класс для всех сервисов в проекте (то есть классов,
    реализующих бизнес-логику для соответствующих обработчиков)
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self.user_dal: UserDAL = UserDAL(db_session=db_session)


class AuthService(BaseService):
    """
    Сервис для работы с авторизацией и аутентификацией пользователя
    """

    async def login(self, email: str, password: str) -> Dict[str, str]:
        user: Optional[User] = await self.user_dal.get_user_by_email(email=email)

        if user is None:
            raise ValueError("User does not exist")

        if not hashing.verify_password(
            hashed_password=user.hashed_password, plain_password=password
        ):
            raise ValueError("Passwords do not match")

        access_token: str = security.create_jwt_token(
            email=user.email,
            exp_timedelta=timedelta(
                minutes=project_settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )
        refresh_token: str = security.create_jwt_token(
            email=user.email,
            exp_timedelta=timedelta(days=project_settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def refresh_token(user: User) -> Dict[str, str]:
        new_access_token: str = security.create_jwt_token(
            email=user.email,
            exp_timedelta=timedelta(
                minutes=project_settings.ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )
        return {"access_token": new_access_token, "token_type": "bearer"}


class UserService(BaseService):
    """
    Сервис для реализации CRUD операций, касающихся пользователя
    """

    async def delete_user(self, user_id: int) -> None:
        user_for_delete = await self.user_dal.get_user_by_id(user_id=user_id)

        if user_for_delete is None:
            raise ValueError("User does not exist")

        if user_for_delete.is_admin:
            raise PermissionError("Cannot delete an admin")

        await self.user_dal.delete_user(user=user_for_delete)

    async def create_user(self, email: str, full_name: str, password: str) -> User:
        new_user = await self.user_dal.create_user(
            email=email,
            full_name=full_name,
            password=hashing.get_password_hash(password),
        )

        return new_user

    async def update_user(
        self, user_id: int, parameters_for_update: Dict[str, str]
    ) -> User:
        user_for_update = await self.user_dal.get_user_by_id(user_id=user_id)

        if user_for_update is None:
            raise ValueError("User does not exist")
        if user_for_update.is_admin:
            raise PermissionError("Cannot update an admin")

        await self.user_dal.update_user(
            user=user_for_update, parameters_for_update=parameters_for_update
        )
        return user_for_update

    async def get_user(self, user_id: int) -> User:
        user: User = await self.user_dal.get_user_by_id(user_id=user_id)

        if user is None:
            raise ValueError("User does not exist")
        if user.is_admin:
            raise PermissionError("Cannot get admin data")

        return user

    async def get_users(self) -> List[User]:
        users: List[User] = await self.user_dal.get_users()
        return users


class AccountService(BaseService):
    """
    Сервис для работы со счетами пользователя
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session=db_session)
        self.account_dal: AccountDAL = AccountDAL(db_session=db_session)

    async def get_current_user_accounts(self, user: User) -> List[Account]:
        accounts: List[Account] = await self.account_dal.get_accounts_by_user_id(
            user_id=user.user_id
        )
        return accounts

    async def get_accounts_by_user_id(self, user_id: int) -> List[Account]:
        target_user: Optional[User] = await self.user_dal.get_user_by_id(
            user_id=user_id
        )
        if target_user is None:
            raise ValueError("User does not exist")
        if target_user.is_admin:
            raise PermissionError("Admin cannot get another admin data")

        accounts: List[Account] = await self.account_dal.get_accounts_by_user_id(
            user_id=user_id
        )
        return accounts


class PaymentService(BaseService):
    """
    Сервис для работы с платежами
    """

    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__(db_session=db_session)
        self.account_dal: AccountDAL = AccountDAL(db_session=db_session)
        self.payment_dal: PaymentDAL = PaymentDAL(db_session=db_session)

    async def process_payment(
        self,
        transaction_id: UUID,
        user_id: int,
        account_id: int,
        amount: float,
        signature: str,
    ) -> None:
        await self._check_user(user_id=user_id)

        account: Account = await self._check_account(
            account_id=account_id, user_id=user_id
        )

        await self._check_payment(
            transaction_id=transaction_id,
            user_id=user_id,
            account_id=account_id,
            amount=amount,
            signature=signature,
        )

        if account is None:
            account: Account = await self.account_dal.create_account(
                account_id=account_id, user_id=user_id
            )

        await self.account_dal.change_balance(account=account, amount=amount)
        await self.payment_dal.add_payment_to_database(
            transaction_id=transaction_id,
            account_id=account_id,
            amount=amount,
            signature=signature,
        )

    async def _check_user(self, user_id: int) -> None:
        user: Optional[User] = await self.user_dal.get_user_by_id(user_id=user_id)

        if user is None:
            raise ValueError("User does not exist")
        if user.is_admin:
            raise PermissionError("Cannot process a payment if the user is an admin")

    async def _check_account(self, account_id: int, user_id: int) -> Account:
        account: Optional[Account] = await self.account_dal.get_account_by_id(
            account_id=account_id
        )
        if account is not None:
            if account.user_id != user_id:
                raise ValueError("Account does not belong to the specified user")

            return account

    async def _check_payment(
        self,
        transaction_id: UUID,
        user_id: int,
        account_id: int,
        amount: float,
        signature: str,
    ) -> None:
        payment: Optional[Payment] = await self.payment_dal.get_payment(
            transaction_id=transaction_id
        )
        if payment is not None:
            raise ValueError("Transaction with this id already exists")

        if not hashing.verify_signature(
            data={
                "transaction_id": transaction_id,
                "user_id": user_id,
                "account_id": account_id,
                "amount": amount,
                "signature": signature,
            }
        ):
            raise ValueError("Signature is incorrect")

    async def get_payments(self, user: User) -> Optional[List[Payment]]:
        accounts: List[Account] = await self.account_dal.get_accounts_by_user_id(
            user_id=user.user_id
        )
        if not accounts:
            []

        payments = []
        for acc in accounts:
            account_payments: List[
                Payment
            ] = await self.payment_dal.get_payments_by_account_id(
                account_id=acc.account_id
            )
            payments.extend(account_payments)

        return payments
