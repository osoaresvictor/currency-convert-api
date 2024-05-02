from datetime import UTC, datetime
from typing import Optional
from app.core.utils import Utils
from app.core.cache import RedisCache
from app.core.settings import Settings
from app.core.logger import Logger
from app.exceptions.currency_code_doesnt_exist_exception import CurrencyCodeDoesntExistException
from app.exceptions.invalid_currency_exception import InvalidCurrencyException
from app.models.currency_conversions_model import CurrencyConversionsModel
from app.repositories.currency_conversions_repository import CurrencyConversionsRepository
from app.api_clients.exchange_rates_api_client import ExchangeRatesApiClient
from app.schemas.currency_conversion_rates_schema import CurrencyConversionRatesSchema


class CurrencyConverterService:
    def __init__(
            self,
            redis_cache: RedisCache,
            exchange_rates_api_client: ExchangeRatesApiClient,
            currency_conversions_repository: CurrencyConversionsRepository
    ):
        self.redis_cache = redis_cache
        self.redis_rate_key_prefix = Settings.REDIS_RATE_KEY_PREFIX
        self.exchange_rates_api_client = exchange_rates_api_client
        self.currency_conversions_repository = currency_conversions_repository

    async def get_conversions_by_user(
        self,
        user_id: str
    ) -> list[CurrencyConversionsModel | None]:
        result = self.currency_conversions_repository.get_conversions_by_user(
            user_id)
        return result

    async def convert_currency_transaction(
        self,
        source_currency_code: str,
        source_currency_value: float,
        target_currency_code: str,
        user_id: str
    ) -> CurrencyConversionsModel:
        source_currency_code = source_currency_code.upper()
        target_currency_code = target_currency_code.upper()

        Utils.validate_currency(source_currency_code, source_currency_value)
        Utils.validate_currency(target_currency_code)

        currency_rates = await self.__fetch_all_conversion_rates(
            source_currency_code, target_currency_code
        )

        for code, rate in currency_rates.rates.items():
            if not rate:
                raise InvalidCurrencyException(code)

        rate_value = 0.0
        try:
            source_currency_rate = currency_rates.rates[source_currency_code]
            target_currency_rate = currency_rates.rates[target_currency_code]
            rate_value = target_currency_rate / source_currency_rate
        except ZeroDivisionError:
            raise InvalidCurrencyException(
                source_currency_code, source_currency_rate)

        currency_conversion_transaction = \
            self.currency_conversions_repository.add_currency_conversion(
                user_id=user_id,
                source_currency_code=source_currency_code,
                source_currency_value=source_currency_value,
                target_currency_code=target_currency_code,
                rate_value=rate_value,
                datetime=datetime.now(UTC)
            )

        return currency_conversion_transaction

    async def __fetch_all_conversion_rates(
            self,
            *currency_codes: str
    ) -> CurrencyConversionRatesSchema:
        Logger.info(f"Get currency conversion rates from API for currencies {
                    currency_codes}")

        result = CurrencyConversionRatesSchema()
        all_conversion_rates: Optional[CurrencyConversionRatesSchema] = None

        for currency_code in currency_codes:
            cache_value = await self.redis_cache.get(
                f'{self.redis_rate_key_prefix}{currency_code}'
            )

            if cache_value:
                result.rates[currency_code] = float(cache_value)
            else:
                if all_conversion_rates is None:
                    all_conversion_rates = self.exchange_rates_api_client.fetch_all_conversion_rates()

                    result_rate = all_conversion_rates.rates.get(
                        currency_code, None)
                    if result_rate is None:
                        raise CurrencyCodeDoesntExistException(
                            currency_code=currency_code)

                    result.rates[currency_code] = result_rate
                    await self.__cache_rates(all_conversion_rates)
                else:
                    result.rates[currency_code] = all_conversion_rates.rates.get(
                        currency_code, None)

        return result

    async def __cache_rates(self, conversion_rates: CurrencyConversionRatesSchema):
        Logger.info("Saving currency conversion rates data in cache")

        exp_seconds = Utils.seconds_until_next_day()
        for code, rate_value in conversion_rates.rates.items():
            is_success = await self.redis_cache.set(
                key=f'{self.redis_rate_key_prefix}{code}',
                value=rate_value,
                exp_seconds=int(exp_seconds)
            )

            if not is_success:
                break
