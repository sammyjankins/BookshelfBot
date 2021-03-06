# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    tele_id = models.CharField(max_length=15)
    last_book = models.ForeignKey('Book', verbose_name='Last book', on_delete=models.SET_NULL, null=True, default='')
    last_shelf = models.ForeignKey('Shelf', verbose_name='Last shelf', on_delete=models.SET_NULL, null=True,
                                   default='')
    state = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} profile'


class BookCase(models.Model):
    title = models.CharField(verbose_name='Название', max_length=100)
    shelf_count = models.IntegerField(default=1)
    section_count = models.IntegerField(default=1)
    row_count = models.IntegerField(default=1)

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
    bookcase = models.ForeignKey(BookCase, verbose_name='Книжный шкаф', on_delete=models.CASCADE,
                                 related_name='shelves')

    owner = models.ForeignKey('auth.User', related_name='shelves', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=150)
    date_of_birth = models.CharField(verbose_name='Дата рождения', max_length=15)
    country = models.CharField(verbose_name='Страна', max_length=100)

    owner = models.ForeignKey('auth.User', related_name='authors', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(verbose_name='Название', max_length=150)
    pages = models.IntegerField(verbose_name='Объем в страницах', default='', blank=True)
    year_of_publication = models.CharField(verbose_name='Год издания', max_length=10, default='', blank=True)
    language = models.CharField(verbose_name='Язык', max_length=50, default='', blank=True)
    ISBN = models.CharField(verbose_name='ISBN', max_length=100)
    type_of_cover = models.CharField(verbose_name='Тип обложки', max_length=25, default='', blank=True)
    read = models.BooleanField(default=False)

    parse_isbn = models.CharField(verbose_name='ISBNp', max_length=100, default='', null=True)

    bookcase = models.ForeignKey(BookCase, verbose_name='Книжный шкаф', on_delete=models.CASCADE,
                                 related_name='books')
    shelf = models.ForeignKey(Shelf, verbose_name='Полка', on_delete=models.CASCADE,
                              related_name='books')
    author = models.ForeignKey(Author, verbose_name='Автор', on_delete=models.CASCADE,
                               related_name='books')

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

    owner = models.ForeignKey('auth.User', related_name='novels', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
