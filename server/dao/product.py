# necessary imports (temp)
from sqlalchemy.orm import Session

from server.dao.models.main import Product

# dao for product model
class ProductDAO:
    def __init__(self, session: Session):
        self.session = session

    # method for add object to database
    def create(self, product: Product):
        self.session.add(product)


    # method for get one object from database by id
    def get_one(self, id):
        return self.session.query(Product).get(id)

    # method for get all objects from database
    def get_all(self):
        return self.session.query(Product).all()

    # method for update data
    def update(self, new_product):
        product = self.session.query(Product).get(new_product.id)

        product.name = new_product.name

        self.session.commit()

    # method for delete object
    def delete(self, id):
        product = self.get_one(id)
        self.session.delete(product)

if __name__ == "__main__":
    pass