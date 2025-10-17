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

    def __repr__(self):
        return f"User(id={self.id}, name={self.username}, password={self.password}, admin={bool(self.admin)}, authorized={bool(self.authorized)})"

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

    def __repr__(self):
        return f"Recipe(id={self.id}, name={self.name}, user_id={self.user_id}...)"



# product model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)

    recipes = relationship("Recipe", secondary=association_table, back_populates="products")

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name})"

if __name__ == "__main__":
    user = User(
        username = "Andrei",
        password = "BhuBhu123",
        admin = 1,
        authorized = 1
    )

    recipe = Recipe(
        name = "test",
        description = "test",
        cooking_time = 1,
        picture_path = "test",
        confirmed = 1,
        user_id = 1
    )

    product = Product(
        name="Test"
    )

    print(user)
    print(recipe)
    print(product)