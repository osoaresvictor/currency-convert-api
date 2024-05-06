from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (Session, declarative_base, scoped_session,
                            sessionmaker)

from app.core.logger import Logger
from app.core.settings import Settings
from app.core.singleton import SingletonMeta

Base = declarative_base()


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.__engine = create_engine(
            Settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False,
        )
        self.__session_factory = sessionmaker(bind=self.__engine)
        self.__session = scoped_session(self.__session_factory)

    @classmethod
    def get_database(cls):
        return cls()

    def get_db_session(self):
        db: Session = self.__session()
        try:
            return db
        except SQLAlchemyError as e:
            Logger.error(f"Error on get db session: {e}")
            raise
        finally:
            db.close()

    def init_db(self):
        Base.metadata.create_all(self.__engine)

    def drop_db(self):
        Base.metadata.drop_all(self.__engine)
