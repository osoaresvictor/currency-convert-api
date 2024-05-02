import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure():
    os.environ["DATABASE_URL"] = "sqlite:///./test_currency_conversion.db"
    os.environ["REDIS_HOST"] = "127.0.0.1"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_DB"] = "1"
    os.environ["API_URL"] = "http://api.exchangeratesapi.io/v1/latest"
    os.environ["API_ACCESS_KEY"] = "ac4c7adf77fee2fd432497b1ea365014"
    os.environ["LOKI_URL"] = "http://127.0.0.1:3100"
    os.environ["LOKI_USER"] = "admin"
    os.environ["LOKI_PASSWORD"] = "admin"
