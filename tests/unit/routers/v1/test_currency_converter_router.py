from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.exceptions.currency_code_doesnt_exist_exception import \
    CurrencyCodeDoesntExistException
from app.exceptions.invalid_currency_exception import InvalidCurrencyException
from app.routers.v1.currency_converter_router import router

app = router


@patch("app.routers.v1.currency_converter_router.CurrencyConverterService")
@patch("app.routers.v1.currency_converter_router.Database")
@patch("app.routers.v1.currency_converter_router.Cache")
@patch("app.routers.v1.currency_converter_router.ExchangeRatesApiClient")
def test_get_conversions_success(
    mock_exchange_client,
    mock_cache,
    mock_db,
    mock_converter_service
):
    # Arrange
    mock_converter_service_instance = mock_converter_service.return_value
    mock_converter_service_instance.get_conversions = Mock(
        return_value=[Mock(to_dict=lambda: {"key": "value"})]
    )
    client = TestClient(app)

    # Act
    response = client.get("/conversions", headers={"user-id": "test_user"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"key": "value"}]


@patch("app.routers.v1.currency_converter_router.CurrencyConverterService")
@patch("app.routers.v1.currency_converter_router.Database")
@patch("app.routers.v1.currency_converter_router.Cache")
@patch("app.routers.v1.currency_converter_router.ExchangeRatesApiClient")
def test_get_conversions_user_not_found(
    mock_exchange_client,
    mock_cache,
    mock_db,
    mock_converter_service
):
    # Arrange
    mock_converter_service_instance = mock_converter_service.return_value
    mock_converter_service_instance.get_conversions = Mock(
        return_value=None
    )

    client = TestClient(app)

    # Act
    with pytest.raises(HTTPException) as exception_raised:
        client.get("/conversions", headers={"user-id": "victor"})

    # Assert
    assert exception_raised.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception_raised.value.detail == "User 'victor' not found"


@patch("app.routers.v1.currency_converter_router.CurrencyConverterService")
@patch("app.routers.v1.currency_converter_router.Database")
@patch("app.routers.v1.currency_converter_router.Cache")
@patch("app.routers.v1.currency_converter_router.ExchangeRatesApiClient")
def test_convert_currency_success(
    mock_exchange_client,
    mock_cache,
    mock_db,
    mock_converter_service
):
    # Arrange
    mock_converter_service_instance = mock_converter_service.return_value
    mock_converter_service_instance.convert_currency_transaction = Mock(
        return_value=Mock(
            transaction_id=1234,
            user_id="test_user",
            source_currency_code="USD",
            source_currency_value=100.0,
            target_currency_code="EUR",
            rate_value=0.85,
            datetime="2024-05-01T10:00:00"
        )
    )

    client = TestClient(app)
    payload = {
        "source_currency_code": "USD",
        "source_currency_value": 100.0,
        "target_currency_code": "EUR",
    }

    # Act
    response = client.post("/convert", json=payload,
                           headers={"user-id": "test_user"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "transaction_id": 1234,
        "user_id": "test_user",
        "source_currency_code": "USD",
        "source_currency_value": 100.0,
        "target_currency_code": "EUR",
        "target_currency_value": 85.0,
        "rate_value": 0.85,
        "datetime": "2024-05-01T10:00:00"
    }


@patch("app.routers.v1.currency_converter_router.CurrencyConverterService")
@patch("app.routers.v1.currency_converter_router.Database")
@patch("app.routers.v1.currency_converter_router.Cache")
@patch("app.routers.v1.currency_converter_router.ExchangeRatesApiClient")
def test_convert_currency_invalid_value(
    mock_exchange_client,
    mock_cache,
    mock_db,
    mock_converter_service
):
    # Arrange
    client = TestClient(app)
    payload = {
        "source_currency_code": "BRL",
        "source_currency_value": 0.05,
        "target_currency_code": "EUR",
    }

    # Act
    with pytest.raises(HTTPException) as exception_raised:
        client.post("/convert", json=payload, headers={"user-id": "test_user"})

    # Assert
    assert exception_raised.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception_raised.value.detail == "The minimum allowed value is 0.1"


@patch("app.routers.v1.currency_converter_router.CurrencyConverterService")
@patch("app.routers.v1.currency_converter_router.Database")
@patch("app.routers.v1.currency_converter_router.Cache")
@patch("app.routers.v1.currency_converter_router.ExchangeRatesApiClient")
def test_convert_currency_invalid_currency_exception(
    mock_exchange_client,
    mock_cache,
    mock_db,
    mock_converter_service
):
    # Arrange
    mock_converter_service_instance = mock_converter_service.return_value
    mock_converter_service_instance.convert_currency_transaction.side_effect = InvalidCurrencyException(
        "Invalid currency")
    client = TestClient(app)
    payload = {
        "source_currency_code": "INVALID",
        "source_currency_value": 100.0,
        "target_currency_code": "BRL",
    }

    # Act
    with pytest.raises(HTTPException) as exception_raised:
        client.post("/convert", json=payload, headers={"user-id": "test_user"})

    # Assert
    assert exception_raised.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exception_raised.value.detail == "Currency code Invalid currency is not valid"


@patch("app.routers.v1.currency_converter_router.CurrencyConverterService")
@patch("app.routers.v1.currency_converter_router.Database")
@patch("app.routers.v1.currency_converter_router.Cache")
@patch("app.routers.v1.currency_converter_router.ExchangeRatesApiClient")
def test_convert_currency_currency_code_doesnt_exist_exception(
    mock_exchange_client,
    mock_cache,
    mock_db,
    mock_converter_service
):
    # Arrange
    mock_converter_service_instance = mock_converter_service.return_value
    mock_converter_service_instance.convert_currency_transaction.side_effect = CurrencyCodeDoesntExistException(
        "ZZZ")
    client = TestClient(app)
    payload = {
        "source_currency_code": "CAD",
        "source_currency_value": 100.0,
        "target_currency_code": "ZZZ",
    }

    # Act
    with pytest.raises(HTTPException) as exception_raised:
        client.post("/convert", json=payload, headers={"user-id": "test_user"})

    # Assert
    assert exception_raised.value.status_code == status.HTTP_404_NOT_FOUND
    assert exception_raised.value.detail == "Currency ZZZ does not exist"
