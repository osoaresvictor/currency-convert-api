from unittest.mock import MagicMock, Mock, patch

import pytest

from app.exceptions.invalid_currency_exception import InvalidCurrencyException
from app.models.currency_conversions_model import CurrencyConversionsModel
from app.schemas.currency_conversion_rates_schema import \
    CurrencyConversionRatesSchema
from app.services.currency_converter_service import CurrencyConverterService


@pytest.fixture
def mock_logger():
    with patch("app.services.currency_converter_service.Logger") as MockLogger:
        yield MockLogger


@pytest.fixture
def service(mock_logger):
    cache = Mock()
    exchange_rates_api_client = MagicMock()
    currency_conversions_repository = MagicMock()

    with patch("app.services.currency_converter_service.Settings") as MockSettings:
        MockSettings.CACHE_RATE_KEY_PREFIX.return_value = "eur-rate-"
        return CurrencyConverterService(
            cache=cache,
            exchange_rates_api_client=exchange_rates_api_client,
            currency_conversions_repository=currency_conversions_repository
        )


def test_get_conversions_no_user_id(service):
    # Arrange
    service._CurrencyConverterService__currency_conversions_repository.list_all_conversions.return_value = []

    # Act
    result = service.get_conversions(user_id=None)

    # Assert
    assert result == []
    service._CurrencyConverterService__currency_conversions_repository.list_all_conversions.assert_called_once()


def test_get_conversions_with_user_id(service):
    # Arrange
    user_id = "123"
    service._CurrencyConverterService__currency_conversions_repository.get_conversions_by_user.return_value = []

    # Act
    result = service.get_conversions(user_id=user_id)

    # Assert
    assert result == []
    service._CurrencyConverterService__currency_conversions_repository.get_conversions_by_user.assert_called_once_with(
        user_id)


def test_convert_currency_transaction_invalid_currency(service):
    # Arrange
    source_currency_code = "BRL"
    source_currency_value = 100.50
    target_currency_code = "INVALID"
    user_id = "user123"

    # Act and Assert
    with pytest.raises(InvalidCurrencyException):
        service.convert_currency_transaction(
            source_currency_code,
            source_currency_value,
            target_currency_code,
            user_id
        )


def test_convert_currency_transaction_success(service):
    # Arrange
    service._CurrencyConverterService__fetch_and_validate_rates = Mock(
        return_value=CurrencyConversionRatesSchema(rates={"USD": 1, "EUR": 0.85}))
    service._CurrencyConverterService__currency_conversions_repository.add_currency_conversion.return_value = CurrencyConversionsModel()

    # Act
    result = service.convert_currency_transaction("USD", 100, "EUR", "123")

    # Assert
    assert isinstance(result, CurrencyConversionsModel)
    service._CurrencyConverterService__currency_conversions_repository.add_currency_conversion.assert_called_once()


def test_fetch_and_validate_rates_cache_hit(service):
    # Arrange
    service._CurrencyConverterService__cache.get.return_value = 1.0

    # Act
    result = service._CurrencyConverterService__fetch_and_validate_rates("USD")

    # Assert
    assert result.rates["USD"] == 1.0
    service._CurrencyConverterService__cache.get.assert_called_once()


def test_fetch_and_validate_rates_cache_miss(service):
    # Arrange
    service._CurrencyConverterService__cache.get.return_value = None
    service._CurrencyConverterService__exchange_rates_api_client.fetch_all_conversion_rates.return_value = CurrencyConversionRatesSchema(
        rates={"USD": 1.0}
    )

    # Act
    result = service._CurrencyConverterService__fetch_and_validate_rates("USD")

    # Assert
    assert result.rates["USD"] == 1.0
    service._CurrencyConverterService__exchange_rates_api_client.fetch_all_conversion_rates.assert_called_once()
