from pybreaker import CircuitBreakerError
import requests
from app.core.http_circuit_breaker import HttpCircuitBreaker
from app.core.logger import Logger
from app.schemas.currency_conversion_rates_schema import CurrencyConversionRatesSchema
from app.core.settings import Settings


class ExchangeRatesApiClient:
    def __init__(self):
        self.__api_url = Settings.API_URL
        self.__access_key = Settings.API_ACCESS_KEY

    def fetch_all_conversion_rates(self) -> CurrencyConversionRatesSchema:
        Logger.info('Start fetching all currency conversion rates')

        try:
            result = HttpCircuitBreaker().fetch_data(
                self.__api_url, params={"access_key": self.__access_key}
            )
            Logger.info('Successfully fetched all currency conversion rates')
            return CurrencyConversionRatesSchema(**result.json())
        except CircuitBreakerError:
            Logger.error("Exchange Rates API currently unavailable.")
        except requests.exceptions.RequestException as e:
            Logger.error(f"An error occurred when fetch data: {e}")
