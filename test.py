from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship
from marshmallow import Schema, fields

engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

assotiation_table = Table(
    'assotiation_table',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('product_id', Integer, ForeignKey('products.id'))
)

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    products = relationship('Product', secondary=assotiation_table, back_populates='recipes')

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    recipes = relationship('Recipe', secondary=assotiation_table, back_populates='products')

prod1 = Product(name='prod1')
prod2 = Product(name='prod2')

recipe = Recipe(name='test_recipe', products=[prod1, prod2])

Base.metadata.create_all(engine)

with Session() as session:
    session.add(recipe)
    session.commit()

    recipe = session.query(Recipe).get(1)
    breakpoint()
    # print([dict(product) for product in recipe.products])