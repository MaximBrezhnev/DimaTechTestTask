from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import database_settings
from src.services.services import UserService, AuthService, AccountService, PaymentService


async def get_db_session() -> AsyncSession:
    try:
        session: AsyncSession = database_settings.async_session()
        yield session
    finally:
        await session.close()


def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(db_session=db_session)


def get_auth_service(db_session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(db_session=db_session)


def get_account_service(db_session: AsyncSession = Depends(get_db_session)) -> AccountService:
    return AccountService(db_session=db_session)


def get_payment_service(db_session: AsyncSession = Depends(get_db_session)) -> PaymentService:
    return PaymentService(db_session=db_session)


