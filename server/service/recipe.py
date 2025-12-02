from typing import List

from server.dao.models.main import Recipe, Product
from server.dao.factory import DAOFactory

# recipe service-class
class RecipeService:
    def __init__(self, factory_dao: DAOFactory) -> None:
        self.factory_dao = factory_dao

    # method for create recipe (long method smell)
    def create(self, product_data: dict) -> Recipe:
        image_data = product_data.pop('image_data')
        username = product_data.pop('user_name')

        with self.factory_dao.user_dao() as user_dao:
            user = user_dao.get_by_username(username)
            user_id = user.id

        product_data['user_id'] = user_id
        products=product_data.pop('products')

        # transform products for adding with relationships
        result_products = []

        for product in products:
            with self.factory_dao.product_dao() as product_dao:
                new_product = product_dao.get_by_name(product)

            if not new_product:
                product_obj = Product(**{'name': product})

                with self.factory_dao.product_dao() as product_dao:
                    product_dao.create(product_obj)
                    new_product = product_dao.get_by_name(product)

            result_products.append(new_product)


        product_data['products'] = result_products

        with self.factory_dao.recipe_dao() as dao:
            recipe = Recipe(**product_data)
            dao.create(recipe)

        return recipe

    # method for get one recipe
    def get_one(self, id: int) -> dict:
        with self.factory_dao.recipe_dao() as dao:
            recipe = dao.get_one(id)
            with self.factory_dao.user_dao() as user_dao:
                user = dao.get_one(recipe.user_id)

            return {
                        'id': recipe.id,
                        'name': recipe.name,
                        'description': recipe.description,
                        'cooking_time': recipe.cooking_time,
                        'picture_path': recipe.picture_path,
                        'confirmed': recipe.confirmed,
                        'user_name': user.name,
                        'products': [product.name for product in recipe.products]
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
                    'user_id': recipe.user_id,
                    'products': [product.name for product in recipe.products]
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
                    'user_id': recipe.user_id,
                    'products': [product.name for product in recipe.products]
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
                with self.factory_dao.user_dao() as user_dao:
                    username = user_dao.get_one(recipe.user_id).username

                result.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'cooking_time': recipe.cooking_time,
                    'picture_path': recipe.picture_path,
                    'confirmed': recipe.confirmed,
                    'user_name': username,
                    'products': [product.name for product in recipe.products]
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
    print(service.get_one(1))
