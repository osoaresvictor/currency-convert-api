from fastapi import APIRouter, status, Depends, HTTPException, Header
from datetime import datetime, UTC
from typing import List

from starlette.responses import JSONResponse

from schemas.currency_conversion_rates_schema import CurrencyConversionRatesSchema
from schemas.currency_conversion_response_schema import CurrencyConversionResponseSchema
from services.currency_converter_service import CurrencyConverterService
from repositories.currency_conversions_repository import CurrencyConversionsRepository
from core.database import Database
from core.utils import Utils

router = APIRouter()


@router.get(
    "/conversions",
    response_model=List[CurrencyConversionResponseSchema],
    description="List all currency conversions performed according to the \
                                                            user_id entered"
)
async def get_conversions(
    user_id: str,
    db: Database = Depends(Database)
):
    repository = CurrencyConversionsRepository(db.session())
    result = repository.get_conversions_by_user(user_id)

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
    source_currency: str,
    source_currency_value: float,
    target_currency: str,
    converter_service: CurrencyConverterService = Depends(CurrencyConverterService),
    db: Database = Depends(Database),
    user_id: str = Header(str)
):
    source_currency = source_currency.upper()
    target_currency = target_currency.upper()

    if not (
        Utils.validate_currency_code_name(source_currency)
        or Utils.validate_currency_code_name(target_currency)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency code must be 3 characters long"
        )

    currency_rates: CurrencyConversionRatesSchema = \
        await converter_service.fetch_conversion_rates(
            source_currency, target_currency
        )

    for currency, rate in currency_rates.rates.items():
        if not rate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency '{currency}' rate not found"
            )

    rate_value: float = 0
    try:
        rate_value = currency_rates.rates[target_currency] / currency_rates.rates[source_currency]
    except ZeroDivisionError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Currency Conversion error, division by zero encountered "
            f"('{source_currency}' = {currency_rates.rates[source_currency]})"
        )

    repository = CurrencyConversionsRepository(db.session())
    currency_conversion_transaction = repository.add_currency_conversion(
        user_id=user_id,
        source_currency=source_currency,
        source_currency_value=source_currency_value,
        target_currency=target_currency,
        rate_value=rate_value,
        datetime=datetime.now(UTC)
    )

    target_currency_value = source_currency_value * rate_value
    return CurrencyConversionResponseSchema(
        transaction_id=currency_conversion_transaction.transaction_id,
        user_id=currency_conversion_transaction.user_id,
        source_currency=currency_conversion_transaction.source_currency,
        source_currency_value=currency_conversion_transaction.source_currency_value,
        target_currency=currency_conversion_transaction.target_currency,
        target_currency_value=target_currency_value,
        rate_value=rate_value,
        datetime=currency_conversion_transaction.datetime
    )
