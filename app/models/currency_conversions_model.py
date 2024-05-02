from sqlalchemy import Float, String, DateTime, Column, Integer
from app.core.database import Base


class CurrencyConversionsModel(Base):
    __tablename__ = 'CurrencyConversions'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    source_currency_code = Column(String(3), nullable=False)
    source_currency_value = Column(Float, nullable=False)
    target_currency_code = Column(String(3), nullable=False)
    rate_value = Column(Float, nullable=False)
    datetime = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'source_currency_code': self.source_currency_code,
            'source_currency_value': self.source_currency_value,
            'target_currency_code': self.target_currency_code,
            'rate_value': self.rate_value,
            'datetime': self.datetime.__str__()
        }
