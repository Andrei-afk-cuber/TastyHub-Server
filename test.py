from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)

input_json = {
    "id":999,
    "username":"john",
    "password":"secret123"
}

schema = UserSchema()
user_obj = schema.load(input_json)

print(user_obj.id)
print(user_obj.username)
print(user_obj.password)