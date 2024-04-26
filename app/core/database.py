from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from core.settings import DATABASE_URL

Base = declarative_base()


class Database:
    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False
        )
        self.session = sessionmaker(bind=self.engine)

    def get_db_session(self):
        db: Session = self.session()
        try:
            yield db
        finally:
            db.close()
