from server.dao.models.main import Product
from server.dao.factory import DAOFactory

# service for product
class ProductService:
    def __init__(self, factory: DAOFactory):
        self.factory_dao = factory

    def create(self, product_data):
        product = Product(**product_data)

        with self.factory_dao.product_dao() as dao:
            dao.create(product)

        return product

    def get_one(self, id):
        with self.factory_dao.product_dao() as dao:
            product = dao.get_one(id)

        return product

    def get_by_name(self, name: str):
        with self.factory_dao.product_dao() as dao:
            product =