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
        self.session.commit()

    # method for get one object from database by id
    def get_one(self, pid):
        return self.session.query(Product).get(pid)

    # method for get product by name
    def get_by_name(self, name):
        return self.session.query(Product).filter(Product.name == name)

    # method for get all objects from database
    def get_all(self):
        return self.session.query(Product).all()

    # method for update data
    def update(self, new_product):
        product = self.session.query(Product).get(new_product['id'])

        if 'name' in new_product:
            product.name = new_product['name']

        self.session.commit()

    # method for delete object
    def delete(self, pid):
        product = self.get_one(pid)
        self.session.delete(product)
        self.session.commit()

if __name__ == "__main__":
    pass