# Generated by Django 5.0.7 on 2024-09-06 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pearlfoods', '0026_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='date_confirmed',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='date_delivered',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='date_shipped',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('received', 'Received'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('on_hold', 'On Hold')], default='received', max_length=10),
        ),
    ]
