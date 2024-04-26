import os

# Server Settings
SERVER_HOST: str = os.getenv("SERVER_HOST")
SERVER_PORT: int = int(os.getenv("SERVER_PORT"))

# Database Settings
DATABASE_URL: str = os.getenv("DATABASE_URL")

# Redis Settings
REDIS_HOST: str = os.getenv("REDIS_HOST")
REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
REDIS_DB: str = os.getenv("REDIS_DB")
REDIS_RATE_KEY_PREFIX: str = 'eur-rate-'

# Security Settings
SECRET_KEY: str = os.getenv("SECRET_KEY")

# Exchange Rates Api Settings
API_URL: str = os.getenv("API_URL")
API_ACCESS_KEY: str = os.getenv("API_ACCESS_KEY")