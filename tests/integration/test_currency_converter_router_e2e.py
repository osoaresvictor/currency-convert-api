from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.core.cache import Cache
from app.core.database import Database
from app.main import app
from app.models.currency_conversions_model import CurrencyConversionsModel


@pytest.fixture(scope="module")
def test_client():
    # Setup
    db = Database()
    db.init_db()
    cache = Cache()
    fastapi_test_client = TestClient(app)

    # Act
    yield fastapi_test_client

    # Teardown
    db.drop_db()
    cache.flush_all()


@pytest.fixture(scope="module")
def setup_database():
    transaction1 = CurrencyConversionsModel()
    transaction1.user_id = "user_test1"
    transaction1.source_currency_code = "AUD"
    transaction1.source_currency_value = 1.5
    transaction1.target_currency_code = "BRL"
    transaction1.rate_value = 3.34785
    transaction1.datetime = datetime.now(UTC)

    transaction2 = CurrencyConversionsModel()
    transaction2.user_id = "user_test2"
    transaction2.source_currency_code = "BRL"
    transaction2.source_currency_value = 2
    transaction2.target_currency_code = "JPY"
    transaction2.rate_value = 30.18965
    transaction2.datetime = datetime.now(UTC)

    with Database().get_db_session() as db_session:
        db_session.add_all([transaction1, transaction2])
        db_session.commit()


def test_get_conversions_user_success_with_user_id_one_transaction_found(test_client, setup_database):
    # Arrange
    user_id_header = "user_test1"

    # Act
    response = test_client.get(
        "/currencyConverter/v1/conversions", headers={"user-id": user_id_header}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()[0].get("user_id") == user_id_header
    assert response.json()[0].get("target_currency_code") == "BRL"


def test_get_conversions_user_success_with_user_id_no_transactions_found(test_client, setup_database):
    # Arrange
    user_id_header = "user_notexist"

    # Act
    response = test_client.get(
        "/currencyConverter/v1/conversions", headers={"user-id": user_id_header}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {'detail': f"User '{user_id_header}' not found"}


def test_get_conversions_user_sucess_without_user_id_two_transactions_found(test_client, setup_database):
    # Act
    response = test_client.get("/currencyConverter/v1/conversions")

    # Assert
    assert response.status_code == 200
    assert response.json()[0].get("user_id") == "user_test1"
    assert response.json()[1].get("user_id") == "user_test2"


def test_convert_currency_success_with_valid_currencies(test_client):
    # Arrange
    payload = {
        "source_currency_code": "AUD",
        "source_currency_value": 1.5,
        "target_currency_code": "JPY"
    }

    # Act
    response_part1 = test_client.post(
        "/currencyConverter/v1/convert",
        json=payload,
        headers={"user-id": "victor"}
    )

    response_part2 = test_client.get(
        "/currencyConverter/v1/conversions", headers={"user-id": "victor"}
    )

    # Assert
    assert response_part1.status_code == 200
    assert response_part1.json().get("source_currency_code") == "AUD"
    assert response_part1.json().get("target_currency_code") == "JPY"
    assert response_part2.status_code == 200
    assert response_part2.json()[0].get("target_currency_code") == "JPY"
