# Generated by Django 3.1.1 on 2020-10-19 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelf', '0002_book_parse_isbn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='language',
            field=models.CharField(default='', max_length=50, verbose_name='Язык'),
        ),
    ]
