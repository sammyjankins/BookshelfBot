# Generated by Django 3.1.1 on 2020-10-21 04:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shelf', '0010_auto_20201021_1109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='barcode',
        ),
    ]
