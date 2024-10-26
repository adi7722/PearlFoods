# Generated by Django 5.0.7 on 2024-07-26 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pearlfoods', '0007_contact_contact_id_order_order_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='IceCreamFlavor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='icecream_flavors/')),
                ('price_250g', models.DecimalField(decimal_places=2, max_digits=6)),
                ('price_500g', models.DecimalField(decimal_places=2, max_digits=6)),
                ('price_1kg', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]
