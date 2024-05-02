from fastapi import APIRouter, status, Depends, HTTPException, Header
from typing import List, Optional
from starlette.responses import JSONResponse

from app.api_clients.exchange_rates_api_client import ExchangeRatesApiClient
from app.core.cache import RedisCache
from app.exceptions.currency_code_doesnt_exist_exception import CurrencyCodeDoesntExistException
from app.exceptions.invalid_currency_exception import InvalidCurrencyException
from app.models.currency_conversions_model import CurrencyConversionsModel
from app.schemas.currency_conversion_response_schema import CurrencyConversionResponseSchema
from app.services.currency_converter_service import CurrencyConverterService
from app.repositories.currency_conversions_repository import CurrencyConversionsRepository
from app.core.database import Database

router = APIRouter()


@router.get(
    "/conversions",
    response_model=List[CurrencyConversionResponseSchema],
    description="List all currency conversions performed according to the \
                                                            user_id entered"
)
async def get_conversions_by_user_id(
    user_id: str,
    db: Database = Depends(Database),
    redis_cache: RedisCache = Depends(RedisCache),
    exchange_rates_api_client: ExchangeRatesApiClient = Depends(
        ExchangeRatesApiClient)
):
    service = CurrencyConverterService(
        redis_cache=redis_cache,
        currency_conversions_repository=CurrencyConversionsRepository(
            db.session()),
        exchange_rates_api_client=exchange_rates_api_client
    )

    result = await service.get_conversions_by_user(user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found"
        )

    return JSONResponse(
        content=[transaction.to_dict() for transaction in result]
    )


@router.post(
    "/convert",
    response_model=CurrencyConversionResponseSchema,
    description="Performs conversion between two different currencies"
)
async def convert_currency(
    source_currency_code: str,
    source_currency_value: float,
    target_currency_code: str,
    user_id: str = Header(str),
    db: Database = Depends(Database),
    redis_cache: RedisCache = Depends(RedisCache),
    exchange_rates_api_client: ExchangeRatesApiClient = Depends(
        ExchangeRatesApiClient)
):
    if source_currency_value < 0.1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The minimum allowed value is 0.1"
        )

    service = CurrencyConverterService(
        redis_cache=redis_cache,
        currency_conversions_repository=CurrencyConversionsRepository(
            db.session()),
        exchange_rates_api_client=exchange_rates_api_client
    )

    transaction: Optional[CurrencyConversionsModel] = None
    try:
        transaction = await service.convert_currency_transaction(
            source_currency_code=source_currency_code,
            source_currency_value=source_currency_value,
            target_currency_code=target_currency_code,
            user_id=user_id
        )
    except InvalidCurrencyException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except CurrencyCodeDoesntExistException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    target_currency_value = source_currency_value * transaction.rate_value
    return CurrencyConversionResponseSchema(
        transaction_id=transaction.transaction_id,
        user_id=transaction.user_id,
        source_currency_code=transaction.source_currency_code,
        source_currency_value=transaction.source_currency_value,
        target_currency_code=transaction.target_currency_code,
        target_currency_value=target_currency_value,
        rate_value=transaction.rate_value,
        datetime=transaction.datetime
    )
