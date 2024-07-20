from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from starlette.responses import JSONResponse

from src.api.user import get_current_user
from src.database.models import User, Payment
from src.dependencies.basic_dependencies import get_payment_service
from src.schemas.schemas import PaymentSchema
from src.services.services import PaymentService

payment_router: APIRouter = APIRouter(
    prefix="/payment",
    tags=["payment", ]
)


@payment_router.get("/", response_model=List[PaymentSchema])
async def get_payments(
        user: User = Depends(get_current_user),
        service: PaymentService = Depends(get_payment_service)
) -> List[Payment]:
    payments: List[Payment] = service.get_payments(user=user)
    if payments is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have payments"
        )

    return payments


@payment_router.post("/")
async def process_payment(
        body: PaymentSchema,
        service: PaymentService = Depends(get_payment_service)
) -> JSONResponse:
    try:
        await service.process_payment(**body.model_dump())
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Payment was successfully processed"}
        )
    except ValueError as exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exception
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot process a payment if the user is an admin"
        )
