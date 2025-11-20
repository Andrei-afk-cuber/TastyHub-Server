from typing import List

from server.dao.models.main import Recipe
from server.dao.factory import DAOFactory

# recipe service-class
class RecipeService:
    def __init__(self, factory_dao: DAOFactory) -> None:
        self.factory_dao = factory_dao

    # method for create recipe
    def create(self, product_data: dict) -> Recipe:
        with self.factory_dao.recipe_dao() as dao:
            recipe = Recipe(**product_data)
            dao.create(recipe)

        return recipe

    # method for get one recipe
    def get_one(self, id: int) -> Recipe:
        with self.factory_dao.recipe_dao() as dao:
            recipe = dao.get_one(id)

        return recipe

    # method for get recipe by name
    def get_by_name(self, name: str) -> List[Recipe]:
        with self.factory_dao.recipe_dao() as dao:
            recipe = dao.get_by_name(name)

        return recipe

    # method for update recipe
    def update(self, recipe_data: dict) -> None:
        with self.factory_dao.recipe_dao() as dao:
            dao.update(recipe_data)

    # method for delete recipe
    def delete(self, id: int) -> None:
        with self.factory_dao.recipe_dao() as dao:
            dao.delete(id)