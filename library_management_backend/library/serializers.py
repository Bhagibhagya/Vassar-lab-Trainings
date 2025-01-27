from rest_framework import serializers
from .models import Author, Book, Borrower, BorrowRecord

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'date_of_birth', 'bio']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'publication_date', 'available_copies', 'total_copies', 'author']
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())  # Ensure this is correctly set
    def create(self, validated_data):
        # Extract nested author data
        author_data = validated_data.pop('author')
        author, created = Author.objects.get_or_create(**author_data)
        book = Book.objects.create(author=author, **validated_data)
        return book
    
class BorrowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrower
        fields = ['id', 'name', 'email', 'phone_number', 'membership_date']

from rest_framework import serializers
from .models import BorrowRecord, Book

class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = ['id', 'borrow_date', 'return_date', 'status', 'book', 'borrower']

    def validate(self, data):
        book = data['book']
        
        # Check if the book has available copies
        if book.available_copies <= 0:
            raise serializers.ValidationError(f"The book '{book.title}' is not available for borrowing.")
        
        return data

    def create(self, validated_data):
        book = validated_data['book']
        
        # Decrease the available copies when a book is borrowed
        if validated_data['status'] == 'borrowed':
            book.available_copies -= 1
            book.save()
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Adjust available copies if status changes to 'returned'
        if instance.status == 'borrowed' and validated_data.get('status') == 'returned':
            instance.book.available_copies += 1
            instance.book.save()
        
        return super().update(instance, validated_data)
