import requests
from pybreaker import CircuitBreakerError

from core.utils import Utils
from core.cache import RedisCache
from core.settings import API_URL, API_ACCESS_KEY, REDIS_RATE_KEY_PREFIX
from core.logger import Logger
from core.http_circuit_breaker import HttpCircuitBreaker
from schemas.currency_conversion_rates_schema import CurrencyConversionRatesSchema


class CurrencyConverterService:
    def __init__(self):
        self.redis_cache = RedisCache()
        self.api_url = API_URL
        self.access_key = API_ACCESS_KEY

    async def fetch_conversion_rates(
            self,
            *currencies: str
    ) -> CurrencyConversionRatesSchema:
        Logger.info(f"Get currency conversion rates for currencies {currencies}")

        result: CurrencyConversionRatesSchema = CurrencyConversionRatesSchema()
        all_conversion_rates = None

        for currency in currencies:
            cache_value = await self.redis_cache.get(
                f'{REDIS_RATE_KEY_PREFIX}{currency}'
            )

            if cache_value:
                result.rates[currency] = float(cache_value)
            else:
                if all_conversion_rates is None:
                    all_conversion_rates = self.__fetch_all_conversion_rates()
                    result.rates[currency] = all_conversion_rates.rates.get(currency, None)
                    await self.__cache_rates(all_conversion_rates)
                else:
                    result.rates[currency] = all_conversion_rates.rates.get(currency, None)

        return result

    async def __cache_rates(self, conversion_rates: CurrencyConversionRatesSchema):
        Logger.info("Saving currency conversion rates data in cache")

        exp_seconds = Utils.seconds_until_next_day()
        for currency_name, rate_value in conversion_rates.rates.items():
            is_success = await self.redis_cache.set(
                key=f'{REDIS_RATE_KEY_PREFIX}{currency_name}',
                value=rate_value,
                exp_seconds=int(exp_seconds)
            )

            if not is_success:
                break

    def __fetch_all_conversion_rates(self) -> CurrencyConversionRatesSchema:
        Logger.info('Start fetching all currency conversion rates')

        try:
            result = HttpCircuitBreaker().fetch_data(
                self.api_url, params={"access_key": self.access_key}
            )
            Logger.info('Successfully fetched all currency conversion rates')
        except CircuitBreakerError:
            print("Exchange Rates API currently unavailable.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred when fetch data: {e}")

        return CurrencyConversionRatesSchema(**result.json())
