# Generated by Django 5.0.7 on 2024-09-16 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pearlfoods', '0038_alter_product_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
