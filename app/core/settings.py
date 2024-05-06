import os

from app.core.singleton import SingletonMeta


class Settings(metaclass=SingletonMeta):
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("Database environment variable not set")

    # Redis Settings
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = os.getenv("REDIS_DB", "0")
    CACHE_RATE_KEY_PREFIX = 'eur-rate-'

    # Exchange Rates Api Settings
    API_URL = os.getenv("API_URL")
    API_ACCESS_KEY = os.getenv("API_ACCESS_KEY")
    if not all([API_URL, API_ACCESS_KEY]):
        raise ValueError(
            "Exchange Rates Api environment variables must be set")

    # Logging Settings
    LOKI_URL = os.getenv("LOKI_URL")
    LOKI_USER = os.getenv("LOKI_USER")
    LOKI_PASSWORD = os.getenv("LOKI_PASSWORD")
    if not all([LOKI_URL, LOKI_USER, LOKI_PASSWORD]):
        raise ValueError("Logging environment variables must be set")
