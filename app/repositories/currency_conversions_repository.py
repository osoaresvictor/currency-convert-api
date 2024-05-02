from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models.currency_conversions_model import CurrencyConversionsModel
from datetime import datetime


class CurrencyConversionsRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_currency_conversion(
        self,
        user_id: str,
        source_currency_code: str,
        source_currency_value: float,
        target_currency_code: str,
        rate_value: float,
        datetime: datetime
    ) -> CurrencyConversionsModel:  # pragma: no cover
        new_conversion = CurrencyConversionsModel(
            user_id=user_id,
            source_currency_code=source_currency_code,
            source_currency_value=source_currency_value,
            target_currency_code=target_currency_code,
            rate_value=rate_value,
            datetime=datetime
        )
        with self.db_session as session:
            session.add(new_conversion)
            session.commit()
            session.refresh(new_conversion)

        return new_conversion

    def get_conversions_by_user(
            self,
            user_id: str
    ) -> list[CurrencyConversionsModel | None]:  # pragma: no cover
        results = self.db_session.execute(
            select(CurrencyConversionsModel)
            .where(CurrencyConversionsModel.user_id == user_id)
        ).scalars().all()

        return results
