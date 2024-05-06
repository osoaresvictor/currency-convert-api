from typing import Optional, Union

import redis

from app.core.logger import Logger
from app.core.settings import Settings
from app.core.singleton import SingletonMeta


class Cache(metaclass=SingletonMeta):
    def __init__(self):
        self.__host = Settings.REDIS_HOST
        self.__port = Settings.REDIS_PORT
        self.__db = Settings.REDIS_DB

        pool = redis.ConnectionPool(
            host=self.__host,
            port=self.__port,
            db=self.__db
        )
        self.__connection = redis.Redis(connection_pool=pool)

    @classmethod
    def get_cache(cls):
        return cls()

    def set(
            self,
            key: str,
            value: Union[str, bytes],
            exp_seconds: Optional[int] = None
    ) -> bool:
        try:
            self.__connection.set(name=key, value=value, ex=exp_seconds)
            return True
        except redis.RedisError as e:
            Logger.error(f"Redis error: {e}")
            return False

    def get(self, key: str) -> Optional[bytes]:
        try:
            return self.__connection.get(key)
        except redis.RedisError as e:
            Logger.error(f"Redis error: {e}")
            return None

    def flush_all(self):
        try:
            return self.__connection.flushall()
        except redis.RedisError as e:
            Logger.error(f"Redis error: {e}")
