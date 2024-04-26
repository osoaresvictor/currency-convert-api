from core.settings import REDIS_HOST, REDIS_PORT, REDIS_DB
import logging
import redis.asyncio as redis


class RedisCache:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        self.__host = host
        self.__port = port
        self.__db = db

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
            logging.error(f"Redis error: {e}")
            return False
        return True

    async def get(self, key):
        try:
            return await self.connection.get(key)
        except redis.RedisError as e:
            logging.error(f"Redis error: {e}")
            return None
