import logging
import logging_loki
from core.singleton import SingletonMeta
from core.settings import LOKI_URL, LOKI_USER, LOKI_PASSWORD


class Logger(metaclass=SingletonMeta):
    _logger_initialized = False

    @classmethod
    def _initialize_logger(cls):
        if not cls._logger_initialized:
            cls.logger = logging.getLogger()
            cls.logger.handlers.clear()
            cls.logger.propagate = False
            cls.logger.setLevel(logging.INFO)

            handler = logging_loki.LokiHandler(
                url=f"{LOKI_URL}/loki/api/v1/push",
                tags={"application": "my-app"},
                auth=(LOKI_USER, LOKI_PASSWORD),
                version="1"
            )

            cls.logger.addHandler(handler)
            cls._logger_initialized = True

    @classmethod
    def info(cls, message):
        cls._initialize_logger()
        cls.logger.info(message)

    @classmethod
    def error(cls, message):
        cls._initialize_logger()
        cls.logger.error(message)
