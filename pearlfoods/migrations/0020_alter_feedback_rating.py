# Generated by Django 5.1 on 2024-09-01 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pearlfoods', '0019_feedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='rating',
            field=models.IntegerField(),
        ),
    ]