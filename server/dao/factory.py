from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.config import DB_URL
from server.dao.models.base import Base
from server.dao.user import UserDAO
from server.dao.recipe import RecipeDAO
from server.dao.product import ProductDAO

# factory for get life-time session control
class DAOFactory:
    def __init__(self, create_tables=True):
        # create engine for session
        self.engine = create_engine(DB_URL)

        # create tables if create_tables == True
        if create_tables:
            self._create_tables_if_needed()

        # create class session for transactions
        self.Session = sessionmaker(self.engine)

    # method that create tables if it needed
    def _create_tables_if_needed(self):
        Base.metadata.create_all(self.engine)

    # context manager for UserDAO
    @contextmanager
    def user_dao(self):
        # create session for transaction
        session = self.Session()
        try:
            yield UserDAO(session)
            # commit if transaction successful
            session.commit()
        except Exception as e:
            # rollback if transaction error
            session.rollback()
            raise
        finally:
            # close session
            session.close()

    # context manager for RecipeDAO
    @contextmanager
    def recipe_dao(self):
        session = self.Session()
        try:
            yield RecipeDAO(session)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    # context manager for product class
    @contextmanager
    def product_dao(self):
        session = self.Session()
        try:
            yield ProductDAO(session)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

# Using factory-class example
if __name__ == "__main__":
    factory = DAOFactory()
    with factory.user_dao() as u:
        print(u.get_by_username('admin'))