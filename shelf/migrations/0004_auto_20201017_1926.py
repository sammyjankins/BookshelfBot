# Generated by Django 3.1.1 on 2020-10-17 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shelf', '0003_auto_20201017_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcase',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Название'),
        ),
    ]