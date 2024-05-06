from pydantic import BaseModel


class CurrencyConversionsRequestSchema(BaseModel):
    source_currency_code: str
    source_currency_value: float
    target_currency_code: str
