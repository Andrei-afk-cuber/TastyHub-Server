# import all necessary libraries
from sqlalchemy import Column, String, Integer, ForeignKey, Table, PrimaryKeyConstraint

from sqlalchemy.orm import relationship

# import dependencies
from server.dao.models.base import Base

# association table
association_table = Table(
    "recipes_products",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
    Column("product_id", ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True),
)

# user model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    admin = Column(Integer, nullable=False, default=0)
    authorized = Column(Integer, nullable=False, default=0)

    recipes = relationship("Recipe", back_populates="user")


# recipe model
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(), nullable=False)
    cooking_time = Column(Integer, nullable=False)
    picture_path = Column(String(), nullable=False)
    confirmed = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    user = relationship("User", back_populates="recipes")
    products = relationship("Product", secondary=association_table, back_populates="recipes")

# product model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    recipes = relationship("Recipe", secondary=association_table, back_populates="products")