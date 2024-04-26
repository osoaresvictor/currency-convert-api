from datetime import datetime
from pydantic import BaseModel


class CurrencyConversionResponseSchema(BaseModel):
    transaction_id: int | None
    user_id: str | None
    source_currency: str | None
    source_currency_value: float | None
    target_currency: str | None
    target_currency_value: float | None
    rate_value: float | None
    datetime: datetime | None
