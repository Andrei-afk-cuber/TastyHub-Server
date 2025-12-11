import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.dao.factory import DAOFactory
from server.dao.models.base import Base
from server.dao.models.main import User


class TestDAOFactory(DAOFactory):
    def __init__(self, create_tables=True):
        # create in-memory database
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )

        if create_tables:
            Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(self.engine)

# factory fixture
@pytest.fixture
def factory():
    factory = TestDAOFactory(create_tables=True)
    yield factory
    # Очистка после теста
    Base.metadata.drop_all(factory.engine)

# test user fixture
@pytest.fixture
def sample_user():
    return User(
        id=1,
        username="testuser",
        password="hashed_password",
        admin=False,
        authorized=True
    )

# user data fixture
@pytest.fixture
def sample_user_data():
    return {
        "username": "newuser",
        "password": "newpass123",
        "admin": False,
        "authorized": True
    }