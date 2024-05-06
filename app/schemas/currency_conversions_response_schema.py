from datetime import datetime

from pydantic import BaseModel


class CurrencyConversionsResponseSchema(BaseModel):
    user_id: str
    transaction_id: int
    source_currency_value: float
    rate_value: float
    target_currency: str
    source_currency: str
    currency_conversions_response_datetime: datetime
