# Generated by Django 5.0.7 on 2024-07-23 21:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pearlfoods', '0005_contact_contact_id_order_order_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='contact_id',
        ),
        migrations.RemoveField(
            model_name='order',
            name='order_id',
        ),
    ]