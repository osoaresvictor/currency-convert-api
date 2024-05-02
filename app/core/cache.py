from app.core.settings import Settings
from app.core.logger import Logger
import redis.asyncio as redis


class RedisCache:
    def __init__(self):
        self.__host = Settings.REDIS_HOST
        self.__port = Settings.REDIS_PORT
        self.__db = Settings.REDIS_DB

        pool = redis.ConnectionPool(
            host=self.__host,
            port=self.__port,
            db=self.__db
        )
        self.connection = redis.Redis(connection_pool=pool)

    async def set(self, key, value, exp_seconds=None):
        try:
            await self.connection.set(name=key, value=value, ex=exp_seconds)
        except redis.RedisError as e:
            Logger.error(f"Redis error: {e}")
            return False
        return True

    async def get(self, key):
        try:
            return await self.connection.get(key)
        except redis.RedisError as e:
            Logger.error(f"Redis error: {e}")
            return None
