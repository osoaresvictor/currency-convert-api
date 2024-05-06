from datetime import UTC, datetime
from typing import Optional

from app.api_clients.exchange_rates_api_client import ExchangeRatesApiClient
from app.core.cache import Cache
from app.core.logger import Logger
from app.core.settings import Settings
from app.core.utils import Utils
from app.exceptions.currency_code_doesnt_exist_exception import \
    CurrencyCodeDoesntExistException
from app.exceptions.invalid_currency_exception import InvalidCurrencyException
from app.models.currency_conversions_model import CurrencyConversionsModel
from app.repositories.currency_conversions_repository import \
    CurrencyConversionsRepository
from app.schemas.currency_conversion_rates_schema import \
    CurrencyConversionRatesSchema


class CurrencyConverterService:
    def __init__(
        self,
        cache: Cache,
        exchange_rates_api_client: ExchangeRatesApiClient,
        currency_conversions_repository: CurrencyConversionsRepository
    ):
        self.__cache = cache
        self.__rate_key_prefix = Settings.CACHE_RATE_KEY_PREFIX
        self.__exchange_rates_api_client = exchange_rates_api_client
        self.__currency_conversions_repository = currency_conversions_repository

    def get_conversions(
        self,
        user_id:
        Optional[str]
    ) -> list[CurrencyConversionsModel]:
        return (self.__currency_conversions_repository.list_all_conversions()
                if user_id is None
                else self.__currency_conversions_repository.get_conversions_by_user(user_id))

    def convert_currency_transaction(
        self,
        source_currency_code: str,
        source_currency_value: float,
        target_currency_code: str,
        user_id: str
    ) -> CurrencyConversionsModel:
        source_currency_code, target_currency_code = \
            source_currency_code.upper(), target_currency_code.upper()
        Utils.validate_currency(source_currency_code)
        Utils.validate_currency(target_currency_code)

        conversion_rates = self.__fetch_and_validate_rates(
            source_currency_code,
            target_currency_code
        )
        rate_value = self.__calculate_conversion_rate(
            conversion_rates,
            source_currency_code,
            target_currency_code
        )

        return self.__currency_conversions_repository.add_currency_conversion(
            user_id=user_id,
            source_currency_code=source_currency_code,
            source_currency_value=source_currency_value,
            target_currency_code=target_currency_code,
            rate_value=rate_value,
            datetime=datetime.now(UTC)
        )

    def __fetch_and_validate_rates(
        self,
        *currency_codes: str
    ) -> CurrencyConversionRatesSchema:
        Logger.info(
            f"Fetching currency conversion rates from API for currencies: {
                currency_codes}"
        )
        result = CurrencyConversionRatesSchema()
        all_conversion_rates = None

        for currency_code in currency_codes:
            cached_rate = self.__cache.get(
                f"{self.__rate_key_prefix}{currency_code}"
            )

            if cached_rate:
                result.rates[currency_code] = float(cached_rate)
            else:
                all_conversion_rates = all_conversion_rates \
                    or self.__exchange_rates_api_client.fetch_all_conversion_rates()
                rate = all_conversion_rates.rates.get(currency_code)

                if rate is None:
                    raise CurrencyCodeDoesntExistException(currency_code)

                result.rates[currency_code] = rate
                self.__cache_rates(all_conversion_rates)

        return result

    def __cache_rates(self, conversion_rates: CurrencyConversionRatesSchema):
        Logger.info("Saving currency conversion rates data in cache")
        exp_seconds = int(Utils.seconds_until_next_day())

        for code, rate in conversion_rates.rates.items():
            if not self.__cache.set(key=f"{self.__rate_key_prefix}{code}", value=rate, exp_seconds=exp_seconds):
                break

    def __calculate_conversion_rate(
        self,
        conversion_rates: CurrencyConversionRatesSchema,
        source_currency_code: str,
        target_currency_code: str
    ) -> float:
        source_rate = conversion_rates.rates.get(source_currency_code)
        target_rate = conversion_rates.rates.get(target_currency_code)

        if not source_rate or not target_rate:
            raise InvalidCurrencyException(
                source_currency_code if not source_rate else target_currency_code)

        try:
            return target_rate / source_rate
        except ZeroDivisionError:
            raise InvalidCurrencyException(source_currency_code, source_rate)
