from marshmallow import Schema, fields

# schema for user model
class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String(required=True)
    password = fields.String(required=True)
    admin = fields.Integer(load_default=0)
    authorized = fields.Integer(load_default=0)

    recipes = fields.Nested("RecipeSchema", many=True, exclude=('user', ))

# schema for recipe model
class RecipeSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True)
    description = fields.String(required=True)
    cooking_time = fields.Integer(required=True)
    picture_path = fields.String(required=True)
    confirmed = fields.Integer(load_default=0)
    user_id = fields.Integer(required=True)

    user = fields.Nested("UserSchema", exclude=("recipes",))
    products = fields.Nested("ProductSchema", many=True, exclude=("recipes", ))

# schema for product schema
class ProductSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True)

    recipes = fields.Nested("RecipeSchema", many=True, exclude=("products", ))