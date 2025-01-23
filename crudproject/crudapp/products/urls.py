from django.urls import path
from .views import ProductAPIView

urlpatterns = [
    path('products/', ProductAPIView.as_view(), name='product_list_create'),  # For listing and creating products
    path('products/<int:pk>/', ProductAPIView.as_view(), name='product_retrieve_update_delete'),  # For retrieving, updating, and deleting a product
]
