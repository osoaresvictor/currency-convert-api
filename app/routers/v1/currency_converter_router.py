from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from starlette.responses import JSONResponse

from app.api_clients.exchange_rates_api_client import ExchangeRatesApiClient
from app.core.cache import Cache
from app.core.database import Database
from app.exceptions.currency_code_doesnt_exist_exception import \
    CurrencyCodeDoesntExistException
from app.exceptions.invalid_currency_exception import InvalidCurrencyException
from app.models.currency_conversions_model import CurrencyConversionsModel
from app.repositories.currency_conversions_repository import \
    CurrencyConversionsRepository
from app.schemas.currency_conversion_response_schema import \
    CurrencyConversionResponseSchema
from app.schemas.currency_conversions_request_schema import \
    CurrencyConversionsRequestSchema
from app.services.currency_converter_service import CurrencyConverterService

router = APIRouter()


@router.get(
    "/conversions",
    response_model=List[CurrencyConversionResponseSchema],
    summary="Get all currency conversions",
    description="List all currency conversions performed. It's possible \
                                                   filter by `user_id` header.",
    tags=["Currency Converter"]
)
async def get_conversions(
    user_id: Optional[str] = Header(None),
    db: Database = Depends(Database.get_database),
    cache: Cache = Depends(Cache.get_cache),
    exchange_rates_api_client: ExchangeRatesApiClient = Depends(
        ExchangeRatesApiClient)
):
    service = CurrencyConverterService(
        cache=cache,
        currency_conversions_repository=CurrencyConversionsRepository(
            db.get_db_session()),
        exchange_rates_api_client=exchange_rates_api_client
    )

    result = service.get_conversions(user_id)
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
    summary="Performs conversion between two different currencies",
    description="Enter the `source_currency_code` and `source_currency_value` \
                         and `target_currency_code` to perform the conversion.",
    tags=["Currency Converter"]
)
async def convert_currency(
    currency_conversions_request: CurrencyConversionsRequestSchema,
    user_id: str = Header(),
    db: Database = Depends(Database.get_database),
    cache: Cache = Depends(Cache.get_cache),
    exchange_rates_api_client: ExchangeRatesApiClient = Depends(
        ExchangeRatesApiClient)
):
    source_currency_code = currency_conversions_request.source_currency_code
    source_currency_value = currency_conversions_request.source_currency_value
    target_currency_code = currency_conversions_request.target_currency_code

    if source_currency_value < 0.1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The minimum allowed value is 0.1"
        )

    service = CurrencyConverterService(
        cache=cache,
        currency_conversions_repository=CurrencyConversionsRepository(
            db.get_db_session()),
        exchange_rates_api_client=exchange_rates_api_client
    )

    transaction: Optional[CurrencyConversionsModel] = None
    try:
        transaction = service.convert_currency_transaction(
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
