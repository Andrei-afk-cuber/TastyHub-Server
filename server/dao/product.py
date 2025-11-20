from typing import List, Optional

# necessary imports (temp)
from sqlalchemy.orm import Session

from server.dao.models.main import Product

# dao for product model
class ProductDAO:
    def __init__(self, session: Session):
        self.session = session

    # method for add object to database
    def create(self, product: Product) -> None:
        self.session.add(product)
        self.session.commit()

    # method for get one object from database by id
    def get_one(self, pid: int) -> Optional[Product]:
        return self.session.query(Product).get(pid)

    # method for get product by name
    def get_by_name(self, name: str) -> Optional[Product]:
        return self.session.query(Product).filter(Product.name == name).first()

    # method for get all objects from database
    def get_all(self) -> List[Product]:
        return self.session.query(Product).all()

    # method for update data
    def update(self, new_product: dict) -> None:
        product = self.session.query(Product).get(new_product['id'])

        if product:
            if 'name' in new_product:
                product.name = new_product['name']

            self.session.commit()

    # method for delete object
    def delete(self, pid: int) -> None:
        product = self.get_one(pid)
        self.session.delete(product)
        self.session.commit()

# code for testing (temp)
if __name__ == "__main__":
    pass