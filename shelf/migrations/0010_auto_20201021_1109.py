# Generated by Django 3.1.1 on 2020-10-21 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelf', '0009_auto_20201020_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='barcode',
            field=models.ImageField(blank=True, default='media/default.jpg', null=True, upload_to='media'),
        ),
    ]
