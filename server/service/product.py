from typing import List

from server.dao.models.main import Product
from server.dao.factory import DAOFactory

# service for product
class ProductService:
    def __init__(self, factory: DAOFactory) -> None:
        self.factory_dao = factory

    # service method for create new product
    def create(self, product_data: dict) -> Product:
        product = Product(**product_data)

        with self.factory_dao.product_dao() as dao:
            dao.create(product)

        return product

    # method for get one product by id
    def get_one(self, pid: int) -> Product:
        with self.factory_dao.product_dao() as dao:
            product = dao.get_one(pid)

        return product

    # method for get one product by name
    def get_by_name(self, name: str) -> Product:
        with self.factory_dao.product_dao() as dao:
            product = dao.get_by_name(name)

        return product

    # method for get all products
    def get_all(self) -> List[Product]:
        with self.factory_dao.product_dao() as dao:
            products = dao.get_all()

        return products

    # method for update product
    def update(self, product_data: dict) -> None:
        with self.factory_dao.product_dao() as dao:
            dao.update(product_data)

    # method for delete product by id
    def delete(self, pid: int) -> None:
        with self.factory_dao.product_dao() as dao:
            dao.delete(pid)