from django.db import models
from django.core.validators import EmailValidator, RegexValidator

class Author(models.Model):
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    bio = models.TextField()

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    available_copies = models.IntegerField(default=0)
    total_copies = models.IntegerField(default=1)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    

    def __str__(self):
        return self.title

class Borrower(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?\d{9,15}$', message="Enter a valid phone number (e.g., +123456789).")]
 )
    membership_date = models.DateField()

    def __str__(self):
        return self.name

class BorrowRecord(models.Model):
    borrow_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('borrowed', 'Borrowed'), ('returned', 'Returned')])
    book = models.ForeignKey(Book, related_name='borrow_records', on_delete=models.CASCADE)
    borrower = models.ForeignKey(Borrower, related_name='borrow_records', on_delete=models.CASCADE)

    def __str__(self):
        return f"Record for {self.book.title} by {self.borrower.name}"
