from rest_framework import serializers
from .models import Item
from .models import Product
from .models import NewProduct  # Serializer for the new product table

class NewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewProduct
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'