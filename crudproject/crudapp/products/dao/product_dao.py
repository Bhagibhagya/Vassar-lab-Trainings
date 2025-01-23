# products/dao/product_dao.py
from ..models import Product

class ProductDAO:
    @staticmethod
    def get_all_products():
        return Product.objects.all()

    @staticmethod
    def get_product_by_id(pk):
        return Product.objects.filter(pk=pk).first()

    @staticmethod
    def create_product(validated_data):
        return Product.objects.create(**validated_data)

    @staticmethod
    def update_product(product, validated_data):
        for key, value in validated_data.items():
            setattr(product, key, value)
        product.save()
        return product

    @staticmethod
    def delete_product(product):
        product.delete()
