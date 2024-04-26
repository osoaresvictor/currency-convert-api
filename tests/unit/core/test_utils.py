import pytest
from datetime import datetime, timedelta

from app.core.utils import Utils


class TestUtils:
    def test_seconds_until_next_day(self):
        # Arrange
        now = datetime.now()
        next_day = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Act
        result = Utils.seconds_until_next_day()

        # Assert
        assert abs(int((next_day - now).total_seconds()) - result) < 10

    @pytest.mark.parametrize("currency_name, expected", [
        ("USD", True),
        ("EU", False),
        ("ABOBORA", False),
        ("", False),
        ("123", False)
    ])
    def test_validate_currency_code_name(self, currency_name, expected):
        assert Utils.validate_currency_code_name(currency_name) == expected
