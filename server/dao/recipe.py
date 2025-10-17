# necessary imports
from sqlalchemy.orm import Session

from server.dao.models.main import Recipe

# dao for recipe model
class RecipeDAO:
    def __init__(self, session: Session):
        self.session = session

    # method for add object to database
    def create(self, user: Recipe):
        pass

    # method for get one object from database by id
    def get_one(self, id):
        pass

    # method for get all objects from database
    def get_all(self):
        pass

    # method for update data
    def update(self, new_user):
        pass

    # method for delete object
    def delete(self, id):
        pass