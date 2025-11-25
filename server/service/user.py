# import libraries
import base64
import hashlib
from typing import List

# imports dependencies
from server.config import PWD_SALT, PWD_ITERATIONS
from server.dao.models.main import User
from server.dao.factory import DAOFactory

# service for user
class UserService:
    def __init__(self, factory_dao: DAOFactory) -> None:
        self.factory_dao = factory_dao

    # service method for create user
    def create(self, user_data: dict) -> User:
        # convert password to hash
        user_data['password'] = self.get_password_hash(user_data['password'])

        with self.factory_dao.user_dao() as dao:
            user = User(**user_data)
            dao.create(user)

        return user

    # service method for get user by id
    def get_one(self, id: int) -> dict:
        with self.factory_dao.user_dao() as dao:
            user = dao.get_one(id)

            return {
                'id':user.id,
                'username':user.username,
                'password':user.password,
                'admin':user.admin,
                'authorized':user.authorized,
            }

    # service method for get user by username
    def get_by_username(self, username: str) -> dict:
        with self.factory_dao.user_dao() as dao:
            user = dao.get_by_username(username)

            return {
                'id':user.id,
                'username':user.username,
                'password':user.password,
                'admin':user.admin,
                'authorized':user.authorized,
            }

    # service method for get all users
    def get_all(self) -> List[dict]:
        result = []
        with self.factory_dao.user_dao() as dao:
            users = dao.get_all()
            for user in users:
                result.append({
                    'id': user.id,
                    'username': user.username,
                    'password': user.password,
                    'admin': user.admin,
                    'authorized': user.authorized
                })

        return result

    # service method for update user
    def update(self, user_data: dict) -> None:
        with self.factory_dao.user_dao() as dao:
            dao.update(user_data)

    # service method for activate user
    def activate(self, user_id: int, activate=True) -> None:
        with self.factory_dao.user_dao() as dao:
            dao.activate(user_id, activate)

    # service method for grant admin privileges
    def grant_admin(self, user_id: int, grant=True) -> None:
        with self.factory_dao.user_dao() as dao:
            dao.grant_admin(user_id, grant)

    # service method for delete user
    def delete(self, id: int) -> None:
        with self.factory_dao.user_dao() as dao:
            dao.delete(id)

    # method for convert password to hash (base64 encoding)
    @staticmethod
    def get_password_hash(password: str) -> bytes:
        hash_digest = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            PWD_SALT,
            PWD_ITERATIONS
        )

        return base64.b64encode(hash_digest)

if __name__ == "__main__":
    factory = DAOFactory()
    service = UserService(factory)
    print(UserService.get_by_username(service, username="admin"))
    print(UserService.get_one(service, id=1))
    print(UserService.get_one(service, id=2))
    print(UserService.get_all(service))