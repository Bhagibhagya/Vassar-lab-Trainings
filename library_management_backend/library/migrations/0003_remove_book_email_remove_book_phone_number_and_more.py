# Generated by Django 4.2.18 on 2025-01-27 10:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_book_email_book_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='email',
        ),
        migrations.RemoveField(
            model_name='book',
            name='phone_number',
        ),
        migrations.AlterField(
            model_name='borrower',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator('^\\+?\\d{9,15}$', message='Enter a valid phone number (e.g., +123456789).')]),
        ),
    ]
