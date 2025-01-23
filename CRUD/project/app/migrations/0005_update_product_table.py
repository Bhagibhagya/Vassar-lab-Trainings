from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_product_table'),  # Previous migration name
    ]

    operations = [
        migrations.AlterModelTable(
            name='product',
            table='product',
        ),
    ]
