from unittest.mock import MagicMock, patch

import pytest
from pybreaker import CircuitBreakerError
from requests.exceptions import RequestException

from app.api_clients.exchange_rates_api_client import ExchangeRatesApiClient
from app.schemas.currency_conversion_rates_schema import \
    CurrencyConversionRatesSchema


@pytest.fixture
def mock_settings():
    with patch("app.api_clients.exchange_rates_api_client.Settings") as MockSettings:
        MockSettings.API_URL = "https://test_api"
        MockSettings.API_ACCESS_KEY = "fake_access_key"
        yield MockSettings


@pytest.fixture
def mock_logger():
    with patch("app.api_clients.exchange_rates_api_client.Logger") as MockLogger:
        yield MockLogger


@pytest.fixture
def mock_http_circuit_breaker():
    with patch(
        "app.api_clients.exchange_rates_api_client.HttpCircuitBreaker"
    ) as MockHttpCircuitBreaker:
        mock_breaker_instance = MockHttpCircuitBreaker.return_value
        yield mock_breaker_instance


def test_fetch_all_conversion_rates_success(mock_settings, mock_logger, mock_http_circuit_breaker):
    # Arrange
    mock_response_data = {
        "base": "BRL",
        "date": "2023-01-01",
        "rates": {"EUR": 0.85, "GBP": 0.75}
    }
    mock_http_circuit_breaker.fetch_data.return_value.json = MagicMock(
        return_value=mock_response_data)
    client = ExchangeRatesApiClient()

    # Act
    result = client.fetch_all_conversion_rates()

    # Assert
    assert isinstance(result, CurrencyConversionRatesSchema)
    assert result.base == "BRL"
    assert result.date == "2023-01-01"
    assert result.rates["EUR"] == 0.85
    assert result.rates["GBP"] == 0.75
    mock_logger.info.assert_called_with(
        'Successfully fetched all currency conversion rates')


def test_fetch_all_conversion_rates_circuit_breaker_error(mock_settings, mock_logger, mock_http_circuit_breaker):
    # Arrange
    mock_http_circuit_breaker.fetch_data.side_effect = CircuitBreakerError
    client = ExchangeRatesApiClient()

    # Act
    result = client.fetch_all_conversion_rates()

    # Assert
    assert result is None
    mock_logger.error.assert_called_with(
        "Exchange Rates API currently unavailable.")


def test_fetch_all_conversion_rates_request_exception(mock_settings, mock_logger, mock_http_circuit_breaker):
    # Arrange
    mock_http_circuit_breaker.fetch_data.side_effect = RequestException(
        "An error occurred")
    client = ExchangeRatesApiClient()

    # Act
    result = client.fetch_all_conversion_rates()

    # Assert
    assert result is None
    mock_logger.error.assert_called_with(
        "An error occurred when fetch data: An error occurred")
