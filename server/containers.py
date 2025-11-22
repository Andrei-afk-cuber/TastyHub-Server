from server.service.user import UserService
from server.service.recipe import RecipeService
from server.service.product import ProductService
from server.dao.factory import DAOFactory
from server.service.schemas.main import UserSchema, ProductSchema, RecipeSchema

# create objects
factory = DAOFactory(create_tables=True)

user_service = UserService(factory)
recipe_service = RecipeService(factory)
product_service = ProductService(factory)

user_schema = UserSchema()
users_schema = UserSchema(many=True)
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)