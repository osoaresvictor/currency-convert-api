from datetime import datetime, timedelta


class Utils:
    @staticmethod
    def seconds_until_next_day() -> int:
        now = datetime.now()
        next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((next_day - now).total_seconds())

    @staticmethod
    def validate_currency_code_name(currency_name: str):
        is_valid_currency = len(currency_name) == 3 and currency_name.isdigit() is False
        return True if is_valid_currency else False
