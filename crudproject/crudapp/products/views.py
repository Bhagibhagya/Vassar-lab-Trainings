from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.product_service import ProductService
from .serializers import ProductSerializer
from django.http import Http404

class ProductAPIView(APIView):
    def get(self, request, pk=None):
        # Retrieve a single product if `pk` is provided
        if pk:
            product = ProductService.retrieve_product(pk)
            if not product:
                raise Http404("Product not found")
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # List all products if no `pk` is provided
        products = ProductService.list_products()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Create a new product
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = ProductService.create_product(serializer.validated_data)
            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # Update a product completely
        product = ProductService.retrieve_product(pk)
        if not product:
            raise Http404("Product not found")
        
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            updated_product = ProductService.update_product(product, serializer.validated_data)
            return Response(ProductSerializer(updated_product).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        # Partially update a product
        product = ProductService.retrieve_product(pk)
        if not product:
            raise Http404("Product not found")
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = ProductService.update_product(product, serializer.validated_data)
            return Response(ProductSerializer(updated_product).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete a product
        product = ProductService.retrieve_product(pk)
        if not product:
            raise Http404("Product not found")
        
        ProductService.delete_product(product)
        return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
