from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.config import DB_URL
from server.dao.models.base import Base

class DAOFactory:
    def __init__(self, create_tables=True):
        self.engine = create_engine(DB_URL, echo=True)

        if create_tables:
            self._create_tables_if_needed()

        self.Session = sessionmaker(self.engine)

    # method that create tables if it needed
    def _create_tables_if_needed(self):
        Base.metadata.create_all(self.engine)

    # context manager for UserDAO
    @contextmanager
    def user_dao(self):
        from server.dao.user import UserDAO
        session = self.Session()
        try:
            yield UserDAO(session)
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    # context manager for RecipeDAO
    @contextmanager
    def recipe_dao(self):
        from server.dao.recipe import RecipeDAO
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
        from server.dao.product import ProductDAO
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

    with factory.user_dao() as user_dao:
        user = user_dao.create(None)