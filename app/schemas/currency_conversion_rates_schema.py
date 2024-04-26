from pydantic import BaseModel
from typing import Dict


class CurrencyConversionRatesSchema(BaseModel):
    success: bool | None = True
    timestamp: int | None = None
    base: str | None = "EUR"
    date: str | None = None
    rates: Dict[str, float] | None = {}
