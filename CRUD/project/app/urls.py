from django.urls import path
from .views import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product
)

urlpatterns = [
    path('', get_products, name='get_products'),                # List all products
    path('<int:pk>/', get_product, name='get_product'),         # Get a product by ID
    path('create/', create_product, name='create_product'),     # Create a new product
    path('update/<int:pk>/', update_product, name='update_product'),  # Update a product
    path('delete/<int:pk>/', delete_product, name='delete_product'),  # Delete a product
]
