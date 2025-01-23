# products/services/product_service.py
from ..dao.product_dao import ProductDAO

class ProductService:
    @staticmethod
    def list_products():
        return ProductDAO.get_all_products()

    @staticmethod
    def retrieve_product(pk):
        return ProductDAO.get_product_by_id(pk)

    @staticmethod
    def create_product(validated_data):
        return ProductDAO.create_product(validated_data)

    @staticmethod
    def update_product(product, validated_data):
        return ProductDAO.update_product(product, validated_data)

    @staticmethod
    def delete_product(product):
        ProductDAO.delete_product(product)
