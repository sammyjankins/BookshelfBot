# Generated by Django 3.1.1 on 2020-10-20 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelf', '0006_auto_20201020_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='barcode',
            field=models.ImageField(blank=True, default='', null=True, upload_to='media'),
        ),
    ]
