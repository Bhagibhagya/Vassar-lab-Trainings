from django.urls import path
from .views import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
    create_new_product,  # New views for NewProduct
    get_new_products,
    get_new_product,
    update_new_product,
    delete_new_product
)

urlpatterns = [
    # URLs for Product
    path('', get_products, name='get_products'),                # List all products
    path('<int:pk>/', get_product, name='get_product'),         # Get a product by ID
    path('create/', create_product, name='create_product'),     # Create a new product
    path('update/<int:pk>/', update_product, name='update_product'),  # Update a product
    path('delete/<int:pk>/', delete_product, name='delete_product'),  # Delete a product
    
    # URLs for NewProduct
    path('new/create/', create_new_product, name='create_new_product'),  # Create a new NewProduct
    path('new/', get_new_products, name='get_new_products'),             # List all NewProducts
    path('new/<int:pk>/', get_new_product, name='get_new_product'),     # Get a NewProduct by ID
    path('new/update/<int:pk>/', update_new_product, name='update_new_product'),  # Update a NewProduct
    path('new/delete/<int:pk>/', delete_new_product, name='delete_new_product'),  # Delete a NewProduct
]
