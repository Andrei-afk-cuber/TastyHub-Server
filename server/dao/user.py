# necessary imports
from sqlalchemy.orm import Session

from server.dao.models.main import User

# dao for user model
class UserDAO:
    def __init__(self, session: Session):
        self.session = session

    # method for add object to database
    def create(self, user: User):
        self.session.add(user)

    # method for get one object from database by id
    def get_one(self, id):
        user = self.session.query(User).get(id)
        return user

    # method for get all objects from database
    def get_all(self):
        users = self.session.query(User).all()
        return users

    # method for update data
    def update(self, new_user: User):
        user = self.session.query(User).get(new_user.id)

        user.username = new_user.username
        user.password = new_user.username
        user.admin = new_user.admin
        user.authorized = new_user.authorized

    # method for delete object
    def delete(self, id):
        user = self.get_one(id)
        self.session.delete(user)

# Test dao
if __name__ == "__main__":
    pass