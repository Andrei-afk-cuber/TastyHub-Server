from marshmallow import Schema, fields

# schema for user model
class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True) # maybe load_only will close password where it is not necessary
    admin = fields.Integer(dump_only=True, load_default=0)
    authorized = fields.Integer(dump_only=True, load_default=0)

    recipes = fields.Nested("RecipeSchema", many=True, exclude=('user', ))

# schema for recipe model
class RecipeSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    cooking_time = fields.Integer(required=True)
    picture_path = fields.String(required=True)
    confirmed = fields.Integer(dump_only=True, load_default=0)
    user_id = fields.Integer(required=True)

    user = fields.Nested("UserSchema", dump_only=True, exclude=("recipes",))
    products = fields.Nested("ProductSchema", many=True, dump_only=True, exclude=("recipes", ))

# schema for product schema
class ProductSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)

    recipes = fields.Nested("RecipeSchema", many=True, dump_only=True, exclude=("products", ))