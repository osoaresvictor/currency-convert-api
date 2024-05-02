from datetime import datetime, timedelta

from app.exceptions.invalid_currency_code_exception import InvalidCurrencyException


class Utils:
    @staticmethod
    def seconds_until_next_day() -> int:
        now = datetime.now()
        next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((next_day - now).total_seconds())

    @staticmethod
    def validate_currency(currency_code: str, currency_rate: float | None = None):
        if type(currency_rate) is float and currency_rate <= 0:
            raise InvalidCurrencyException(currency_code=currency_code)

        if len(currency_code) != 3 or currency_code.isalpha() is False:
            raise InvalidCurrencyException(currency_code=currency_code)
