from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['name']  # Orders by name in ascending order
        verbose_name = 'Product Item'  # Custom singular name
        verbose_name_plural = 'Product Items'  # Custom plural name
class SQLUser(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
from djongo import models

class NoSQLProduct(models.Model):
    name = models.CharField(max_length=255)
    details = models.JSONField()  # MongoDB supports JSON fields natively
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

