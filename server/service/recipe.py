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
            product_data['confirmed'] = 0
            recipe = Recipe(**product_data)
            dao.create(recipe)

        return recipe

    # method for get one recipe
    def get_one(self, id: int) -> dict:
        with self.factory_dao.recipe_dao() as dao:
            recipe = dao.get_one(id)

            return {
                        'id': recipe.id,
                        'name': recipe.name,
                        'description': recipe.description,
                        'cooking_time': recipe.cooking_time,
                        'picture_path': recipe.picture_path,
                        'confirmed': recipe.confirmed,
                        'user_id': recipe.user_id
                    }

    # method for get recipe by name
    def get_by_name(self, name: str) -> list:
        result = []
        with self.factory_dao.recipe_dao() as dao:
            recipes = dao.get_by_name(name)

            for recipe in recipes:
                result.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'cooking_time': recipe.cooking_time,
                    'picture_path': recipe.picture_path,
                    'confirmed': recipe.confirmed,
                    'user_id': recipe.user_id
                })

        return result

    def get_by_ingredients(self, ingredients: List[str]) -> List[dict]:
        result = []
        with self.factory_dao.recipe_dao() as dao:
            recipes = dao.get_by_ingredients(ingredients)

            if not recipes:
                raise Exception('No recipes found')

            for recipe in recipes:
                result.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'cooking_time': recipe.cooking_time,
                    'picture_path': recipe.picture_path,
                    'confirmed': recipe.confirmed,
                    'user_id': recipe.user_id
                })

        return result

    # method for get all recipes
    def get_all(self, only_confirmed=True):
        result = []
        with self.factory_dao.recipe_dao() as dao:
            recipes = dao.get_all(only_confirmed=only_confirmed)

            if not recipes:
                raise Exception('No recipes found')

            for recipe in recipes:
                result.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'cooking_time': recipe.cooking_time,
                    'picture_path': recipe.picture_path,
                    'confirmed': recipe.confirmed,
                    'user_id': recipe.user_id
                })

        return result

    # method for confirm recipe
    def confirm(self, recipe_id, confirm=True):
        with self.factory_dao.recipe_dao() as dao:
            dao.confirm(recipe_id, confirm)

    # method for update recipe
    def update(self, recipe_data: dict, by_admin: bool = False) -> None:
        if not by_admin:
            recipe_data['confirmed'] = 0

        with self.factory_dao.recipe_dao() as dao:
            dao.update(recipe_data)

    # method for delete recipe
    def delete(self, id: int) -> None:
        with self.factory_dao.recipe_dao() as dao:
            dao.delete(id)

# debugger run
if __name__ == '__main__':
    factory = DAOFactory()
    service = RecipeService(factory)
    print(RecipeService.get_all(service))