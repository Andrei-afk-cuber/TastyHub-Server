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
        self.session.commit()

    # method for get one object from database by id
    def get_one(self, id):
        return self.session.query(User).get(id)

    # method for get all objects from database
    def get_all(self):
        return self.session.query(User).all()

    # method for get user by username
    def get_by_username(self, username):
        return self.session.query(User).filter(User.username == username).first()

    # method for update data
    def update(self, new_user_data):
        user = self.session.query(User).get(new_user_data['id'])

        if 'username' in new_user_data:
            user.username = new_user_data['username']
        if 'password' in new_user_data:
            user.password = new_user_data['password']
        if 'admin' in new_user_data:
            user.admin = new_user_data['admin']
        if 'authorized' in new_user_data:
            user.authorized = new_user_data['authorized']

        self.session.commit()

    # method for delete object
    def delete(self, id):
        user = self.get_one(id)
        self.session.delete(user)
        self.session.commit()

# Test dao
if __name__ == "__main__":
    pass