# necessary imports
from sqlalchemy.orm import Session

from server.dao.models.main import Recipe

# dao for recipe model
class RecipeDAO:
    def __init__(self, session: Session):
        self.session = session

    # method for add object to database
    def create(self, recipe: Recipe):
        self.session.add(recipe)
        self.session.commit()

    # method for get one object from database by id
    def get_one(self, id):
        return self.session.query(Recipe).get(id)

    # method for get recipe by name
    def get_by_name(self, name):
        return self.session.query(Recipe).filter(Recipe.name == name)

    # method for get all objects from database
    def get_all(self):
        return self.session.query(Recipe).all()

    # method for update data
    def update(self, new_recipe_data):
        recipe = self.session.query(Recipe).get(new_recipe_data['id'])

        if 'name' in new_recipe_data:
            recipe.name = new_recipe_data['name']
        if 'description' in new_recipe_data:
            recipe.description = new_recipe_data['description']
        if 'cooking_time' in new_recipe_data:
            recipe.cooking_time = new_recipe_data['cooking_time']
        if 'picture_path' in new_recipe_data:
            recipe.picture_path = new_recipe_data['picture_path']
        if 'confirmed' in new_recipe_data:
            recipe.confirmed = new_recipe_data['confirmed']

        self.session.commit()

    # method for delete object
    def delete(self, id):
        recipe = self.session.query(Recipe).get(id)
        self.session.delete(recipe)
        self.session.commit()