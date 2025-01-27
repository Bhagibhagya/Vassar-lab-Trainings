from rest_framework import generics,filters
from .models import Author, Book, Borrower, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, BorrowerSerializer, BorrowRecordSerializer
from django.utils.timezone import now
from rest_framework.response import Response

class AuthorListCreate(generics.ListCreateAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class AuthorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author__name']


class BookDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BorrowerListCreate(generics.ListCreateAPIView):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer

class BorrowerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Borrower.objects.all()
    serializer_class = BorrowerSerializer

class BorrowRecordListCreate(generics.ListCreateAPIView):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

class BorrowRecordDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer

class OverdueBooksView(generics.ListAPIView):
    serializer_class = BorrowRecordSerializer

    def get_queryset(self):
        return BorrowRecord.objects.filter(return_date__lt=now(), status='borrowed')