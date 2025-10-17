from marshmallow import Schema, fields

class TestClass:
    def __init__(self, id, word):
        self.id = id
        self.word = word

class TestSchema(Schema):
    id = fields.Integer()
    word = fields.String()

obj = TestClass(id=1, word="Hello, world")

res = TestSchema().dump(obj)

print(type(res))
print(res)

res = TestSchema().load(res)

print(type(res))
print(res)