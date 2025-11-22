from marshmallow import Schema, fields, post_load
from dataclasses import dataclass

class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String(required=True)
    password = fields.String(required=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)

@dataclass
class User:
    id: int = 1
    username: str = "test_user"
    password: str = 'QwErTy'

user = User()

user = UserSchema().dumps(user)
print(type(user))
print(user)