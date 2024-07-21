from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from starlette.responses import JSONResponse

from src.api.user import get_current_user
from src.database.models import Payment
from src.database.models import User
from src.dependencies.basic_dependencies import get_payment_service
from src.schemas.schemas import PaymentSchema
from src.schemas.schemas import ShowPaymentSchema
from src.services.services import PaymentService

payment_router: APIRouter = APIRouter(
    prefix="/payment",
    tags=[
        "payment",
    ],
)


@payment_router.get("/", response_model=List[ShowPaymentSchema])
async def get_payments(
    user: User = Depends(get_current_user),
    service: PaymentService = Depends(get_payment_service),
) -> List[Payment]:
    """
    Обработчик, отвечающий за получение авторизованным пользователем связанных с собой платежей.
    Данные о пользователе берутся из заголовков запроса

    В случае, если платежи пытается получить администратор, возникает исключение с кодом 403

    В случае, если текущий пользователь не имеет связанных со своими счетами платежей, возникает исключение с кодом 404

    В противном случае возвращается список с подробной информацией о каждом платеже, связанном с пользователем
    """

    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin cannot have payments"
        )

    payments: List[Payment] = await service.get_payments(user=user)
    if not payments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not have payments"
        )

    return payments


@payment_router.post("/")
async def process_payment(
    body: PaymentSchema, service: PaymentService = Depends(get_payment_service)
) -> JSONResponse:
    """
    Обработчик, реализующий обработку поступившего платежа

    В случае появления проблем, связанных с данными платежа, возникает исключение с кодом 400

    В случае, если пользователь, которому адресован платеж, является администратором, возникает исключение с кодом 403

    В противном случае транзакция выполняется, записывается в базу данных и возвращается сообщение о ее успешности
    """

    try:
        await service.process_payment(**body.model_dump())
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Payment was successfully processed"},
        )
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exception)
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot process a payment if the user is an admin",
        )
