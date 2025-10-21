from server.dao.models.main import Product
from server.dao.factory import DAOFactory

# service for product
class ProductService:
    def __init__(self, factory: DAOFactory):
        self.factory_dao = factory

    # service method for create new product
    def create(self, product_data):
        product = Product(**product_data)

        with self.factory_dao.product_dao() as dao:
            dao.create(product)

        return product

    # method for get one product by id
    def get_one(self, pid):
        with self.factory_dao.product_dao() as dao:
            product = dao.get_one(pid)

        return product

    # method for get one product by name
    def get_by_name(self, name: str):
        with self.factory_dao.product_dao() as dao:
            product = dao.get_by_name(name)

    # method for get all products
    def get_all(self):
        with self.factory_dao.product_dao() as dao:
            products = dao.get_all()

        return products

    # method for update product
    def update(self, product_data):
        with self.factory_dao.product_dao() as dao:
            dao.update(product_data)

    # method for delete product by id
    def delete(self, pid):
        with self.factory_dao.product_dao() as dao:
            dao.delete(pid)