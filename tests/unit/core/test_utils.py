from datetime import datetime
from unittest.mock import patch

import pytest

from app.core.utils import Utils
from app.exceptions.invalid_currency_exception import InvalidCurrencyException


@patch('app.core.utils.datetime')
def test_seconds_until_next_day(mock_datetime):
    # Arrange
    mock_now = datetime(2024, 5, 1, 0, 0)
    mock_datetime.now.return_value = mock_now

    # Act
    result = Utils.seconds_until_next_day()

    # Assert
    expected_seconds = int((datetime(2024, 5, 2) - mock_now).total_seconds())
    assert abs(result - expected_seconds) < 30


def test_validate_currency_invalid_rate():
    # Arrange
    invalid_rate = -1.0
    currency_code = "BRL"

    # Act & Assert
    with pytest.raises(InvalidCurrencyException):
        Utils.validate_currency(currency_code, invalid_rate)


def test_validate_currency_invalid_code_length():
    # Arrange
    invalid_code = "JP"
    valid_rate = 1.0

    # Act & Assert
    with pytest.raises(InvalidCurrencyException):
        Utils.validate_currency(invalid_code, valid_rate)


def test_validate_currency_invalid_code_contains_number():
    # Arrange
    invalid_code = "BR8"
    valid_rate = 1.0

    # Act & Assert
    with pytest.raises(InvalidCurrencyException):
        Utils.validate_currency(invalid_code, valid_rate)


def test_validate_currency_valid_code_and_rate():
    # Arrange
    valid_code = "BRL"
    valid_rate = 1.0

    # Act
    result = Utils.validate_currency(valid_code, valid_rate)

    # Assert
    assert result is None
