# Generated by Django 5.0.7 on 2024-09-16 20:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pearlfoods', '0036_alter_cart_session_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='icecream_flavors/Upload')),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=6)),
                ('unit', models.CharField(choices=[('g', 'Gram'), ('l', 'Liter')], default='g', max_length=10)),
                ('category', models.CharField(choices=[('Masala', 'Masala'), ('Atta', 'Atta'), ('Home Remedies', 'Home Remedies'), ('Honey', 'Honey'), ('Oil', 'Oil'), ('Recipes', 'Recipes')], default='Masala', max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='flavor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pearlfoods.product'),
        ),
        migrations.DeleteModel(
            name='MasalaFlavor',
        ),
    ]
