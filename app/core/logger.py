import logging
from multiprocessing import Queue

import logging_loki

from app.core.settings import Settings
from app.core.singleton import SingletonMeta


class Logger(metaclass=SingletonMeta):
    _logger_initialized = False

    @classmethod
    def _initialize_logger(cls):
        if not cls._logger_initialized:
            handler = logging_loki.LokiQueueHandler(
                Queue(-1),
                url=f"{Settings.LOKI_URL}/loki/api/v1/push",
                tags={"application": "currency-converter-api-app"},
                auth=(Settings.LOKI_USER, Settings.LOKI_PASSWORD),
                version="1"
            )

            cls.logger = logging.getLogger()
            cls.logger.addHandler(handler)
            cls.logger.setLevel(logging.INFO)
            cls._logger_initialized = True

    @classmethod
    def info(cls, message):
        cls._initialize_logger()
        cls.logger.info(message)

    @classmethod
    def error(cls, message):
        cls._initialize_logger()
        cls.logger.error(message)
