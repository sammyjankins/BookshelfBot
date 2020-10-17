# from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models

# User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tele_id = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.user.username} profile'


class BookCase(models.Model):
    title = models.CharField(verbose_name='Название', max_length=100)
    # user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    # trying to auth stuff
    owner = models.ForeignKey('auth.User', related_name='bookcases', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Shelf(models.Model):
    title = models.CharField(verbose_name='Название', max_length=100)
    ROWS = (
        ('Первый', 'Первый'),
        ('Второй', 'Второй'),
        ('Третий', 'Третий'),
        ('Четвертый', 'Четвертый'),
    )
    row = models.CharField(verbose_name='Ряд', max_length=100, choices=ROWS, default='')
    # row = models.IntegerField(verbose_name='Ряды', choices=ROWS, default='')
    bookcase = models.ForeignKey(BookCase, verbose_name='Книжный шкаф', on_delete=models.CASCADE,
                                 related_name='shelves')

    # trying to auth stuff
    owner = models.ForeignKey('auth.User', related_name='shelves', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=150)
    date_of_birth = models.CharField(verbose_name='Дата рождения', max_length=15)
    country = models.CharField(verbose_name='Страна', max_length=100)

    # trying to auth stuff
    owner = models.ForeignKey('auth.User', related_name='authors', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(verbose_name='Название', max_length=150)
    pages = models.IntegerField(verbose_name='Объем в страницах')
    year_of_publication = models.CharField(verbose_name='Год издания', max_length=10)
    language = models.CharField(verbose_name='Язык', max_length=50)
    ISBN = models.CharField(verbose_name='ISBN', max_length=100)
    type_of_cover = models.CharField(verbose_name='Тип обложки', max_length=15)
    read = models.BooleanField(default=False)

    bookcase = models.ForeignKey(BookCase, verbose_name='Книжный шкаф', on_delete=models.CASCADE,
                                 related_name='books')
    shelf = models.ForeignKey(Shelf, verbose_name='Полка', on_delete=models.CASCADE,
                              related_name='books')
    author = models.ForeignKey(Author, verbose_name='Автор', on_delete=models.CASCADE,
                               related_name='books')

    # trying to auth stuff
    owner = models.ForeignKey('auth.User', related_name='books', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Novel(models.Model):
    title = models.CharField(max_length=100, blank=False)
    year_of_creation = models.CharField(max_length=100, blank=False)
    original_language = models.CharField(max_length=100, blank=False)
    genre_tags = models.CharField(max_length=100, blank=False)
    read = models.BooleanField(default=False)

    author = models.ForeignKey(Author, verbose_name='Автор', on_delete=models.CASCADE,
                               related_name='novels')

    book = models.ForeignKey(Book, verbose_name='Книга', on_delete=models.CASCADE,
                             related_name='novels')

    # trying to auth stuff
    owner = models.ForeignKey('auth.User', related_name='novels', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
