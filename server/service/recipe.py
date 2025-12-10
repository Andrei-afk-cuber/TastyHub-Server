import base64
import io
import os
from PIL import Image
from typing import List
from pathlib import Path

from server.dao.models.main import Recipe, Product
from server.dao.factory import DAOFactory
from server.config import IMAGE_PATH

# recipe service-class
class RecipeService:
    def __init__(self, factory_dao: DAOFactory) -> None:
        self.factory_dao = factory_dao

    # method for create recipe
    def create(self, product_data: dict) -> Recipe:
        self._save_recipe_image(product_data)
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
                user = user_dao.get_one(recipe.user_id)
                return {
                            'id': recipe.id,
                            'name': recipe.name,
                            'description': recipe.description,
                            'cooking_time': recipe.cooking_time,
                            'picture_path': recipe.picture_path,
                            'confirmed': recipe.confirmed,
                            'user_name': user.username,
                            'products': [product.name for product in recipe.products]
                        }

    # method for get recipe by name
    def get_by_username(self, username: str) -> list:
        result = []
        with self.factory_dao.recipe_dao() as dao:
            recipes = dao.get_by_username(username)

            for recipe in recipes:
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

    # method for get recipe by name
    def get_by_name(self, name: str) -> list:
        result = []
        with self.factory_dao.recipe_dao() as dao:
            recipes = dao.get_by_name(name)

            for recipe in recipes:
                with self.factory_dao.user_dao() as user_dao:
                    user = user_dao.get_one(recipe.user_id)

                    result.append({
                                'id': recipe.id,
                                'name': recipe.name,
                                'description': recipe.description,
                                'cooking_time': recipe.cooking_time,
                                'picture_path': recipe.picture_path,
                                'confirmed': recipe.confirmed,
                                'user_name': user.username,
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
                with self.factory_dao.user_dao() as user_dao:
                    user = user_dao.get_one(recipe.user_id)

                    result.append({
                        'id': recipe.id,
                        'name': recipe.name,
                        'description': recipe.description,
                        'cooking_time': recipe.cooking_time,
                        'picture_path': recipe.picture_path,
                        'confirmed': recipe.confirmed,
                        'user_name': user.username,
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
                image_data = self._convert_image_to_bytes(recipe)
                result.append({
                    'id': recipe.id,
                    'name': recipe.name,
                    'description': recipe.description,
                    'cooking_time': recipe.cooking_time,
                    'picture_path': recipe.picture_path,
                    'image_data': image_data,
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

    # method for save image
    @staticmethod
    def _save_recipe_image(recipe_data: dict) -> str:
        try:
            if 'image_data' not in recipe_data:
                raise ValueError('image_data is not exists in recipe_data')

            if 'picture_path' not in recipe_data:
                raise ValueError('picture_path is not exists in recipe_data')

            image_data = recipe_data['image_data']
            picture_path = recipe_data['picture_path']

            if not image_data:
                raise ValueError('image_data is empty')

            if not picture_path:
                raise ValueError('picture_path is empty')

            filename = Path(picture_path).name
            save_path = IMAGE_PATH / filename

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            if image.mode != 'RGB':
                image = image.convert('RGB')

            max_size = (800, 800)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.LANCZOS)

            image.save(save_path, format="JPEG", quality=85, optimize=True)

            if not save_path.exists():
                raise IOError(f'save path {save_path} does not exist')

            return filename

        except Exception as e:
            print(f"Error: {e}")

    def _convert_image_to_bytes(self, recipe: Recipe) -> bytes:
        image_filename = recipe.picture_path

        project_root = Path.cwd()
        image_dir = project_root / "recipe_images"
        image_path = image_dir / image_filename

        if not os.path.exists(image_path):
            os.mkdir(image_dir)

        img = Image.open(image_path)
        max_size = (800, 800)
        img.thumbnail(max_size, Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return image_data


# debugger run
if __name__ == '__main__':
    factory = DAOFactory()
    service = RecipeService(factory)
    print(service.get_one(1))
