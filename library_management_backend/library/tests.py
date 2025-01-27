from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from library.models import Author, Book, Borrower, BorrowRecord


class LibraryAPITestCase(APITestCase):
    def setUp(self):
        # Create sample author
        self.author = Author.objects.create(
            name="Jane Doe",
            date_of_birth="1980-01-01",
            bio="A well-known author."
        )
        
        # Create sample book
        self.book = Book.objects.create(
            title="Sample Book",
            isbn="1234567890123",
            publication_date="2023-01-01",
            available_copies=5,
            total_copies=5,
            author=self.author
        )
        
        # Create sample borrower
        self.borrower = Borrower.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            phone_number="+123456789",
            membership_date="2024-01-01"
        )
        
        # API endpoints
        self.book_list_url = reverse("book-list-create")
        self.book_detail_url = reverse("book-detail", kwargs={"pk": self.book.id})
        self.borrower_list_url = reverse("borrower-list-create")

    def test_list_books(self):
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Ensure the created book is listed

    def test_create_book(self):
        # Ensure the author exists before sending the request
        self.assertTrue(Author.objects.filter(id=self.author.id).exists())  # Check if author is created correctly

        payload = {
            "title": "New Book",
            "isbn": "9876543210123",
            "publication_date": "2023-05-01",
            "available_copies": 10,
            "total_copies": 10,
            "author": self.author.id  # Ensure this is correctly referencing the author's ID
        }

        response = self.client.post(self.book_list_url, data=payload)

        # Print the response data for debugging
        print(response.data)

        # Check if the status code is 201 (Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the book is added to the database
        self.assertEqual(Book.objects.count(), 2)  # One additional book should be created

        # Validate specific fields in the response
        self.assertEqual(response.data["title"], "New Book")
        self.assertEqual(response.data["isbn"], "9876543210123")
        self.assertEqual(response.data["available_copies"], 10)
        self.assertEqual(response.data["total_copies"], 10)
        self.assertEqual(response.data["author"], self.author.id)  # Ensure the correct author ID is returned

    def test_borrow_book(self):
        payload = {
            "borrow_date": "2025-01-28",
            "status": "borrowed",
            "book": self.book.id,
            "borrower": self.borrower.id
        }
        response = self.client.post(reverse("borrowrecord-list-create"), data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)  # Ensure available copies decrease

    def test_borrow_book_no_copies(self):
        self.book.available_copies = 0
        self.book.save()
        payload = {
            "borrow_date": "2025-01-28",
            "status": "borrowed",
            "book": self.book.id,
            "borrower": self.borrower.id
        }
        response = self.client.post(reverse("borrowrecord-list-create"), data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_in_borrower(self):
        payload = {
            "name": "Invalid Borrower",
            "email": "invalid_email",
            "phone_number": "+123456789",
            "membership_date": "2025-01-01"
        }
        response = self.client.post(self.borrower_list_url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Enter a valid email address.", response.data["email"])
