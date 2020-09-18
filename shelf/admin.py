from django.contrib import admin

from shelf.models import BookCase, Book, Shelf, Author, Novel, Profile

admin.site.register([BookCase, Book, Shelf, Author, Novel, Profile])
