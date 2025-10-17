# import libraries
import base64
import hashlib

# imports dependencies
from server.config import PWD_SALT, PWD_ITERATIONS
from server.dao.user import UserDAO
from server.dao.models.main import User
from server.dao.factory import DAOFactory

# service for user
class UserService:
    def __init__(self, factory_dao: DAOFactory):
        self.factory_dao = factory_dao

    # service method for create user
    def create(self, user_data):
        # convert password to hash
        user_data['password'] = self.get_password_hash(user_data['password'])

        with self.factory_dao.user_dao() as dao:
            user = User(**user_data)
            dao.create(user)

        return user

    # service method for get user by id
    def get_one(self, id: int):
        with self.factory_dao.user_dao() as dao:
            user = dao.get_one(id)

        return user

    # service method for get user by username
    def get_by_username(self, username: str):
        with self.factory_dao.user_dao() as dao:
            user = dao.get_by_username(username)

        return user

    # service method for get all users
    def get_all(self):
        with self.factory_dao.user_dao() as dao:
            users = dao.get_all()

        return users

    # service method for update user
    def update(self, user_data):
        new_user = User(**user_data)

        with self.factory_dao.user_dao() as dao:
            dao.update(new_user)

        return new_user

    # method for convert password to hash (base64 encoding)
    def get_password_hash(self, password: str):
        hash_digest = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            PWD_SALT,
            PWD_ITERATIONS
        )

        return base64.b64encode(hash_digest)