from django.db.models import Q
from pyngrok import ngrok

from shelf.models import Profile, Book

words = {
    '1': 'один',
    '2': 'два',
    '3': 'три',
    '4': 'четыре',
    '5': 'пять',
    '6': 'шесть',
    '7': 'семь',
    '8': 'восемь',
    '9': 'девять',
    '10': 'десять',
    '11': 'одиннадцать',
    '12': 'двенадцать',
    '13': 'тринадцать',
    '14': 'четырнадцать',
    '15': 'пятнадцать',
    '16': 'шестнадцать',
    '17': 'семнадцать',
    '18': 'восемнадцать',
    '19': 'девятнадцать',
    '20': 'двадцать',
}


def num_to_words(text):
    values = text.split()
    try:
        result = [value if not value.isdigit() else words[value] for value in values]
        return ' '.join(result)
    except Exception as e:
        print('not in dict')
        return text


def set_last_book(user, book):
    user.last_book = book
    user.save()


def get_last_book(chat_id):
    profile = Profile.objects.get(tele_id=chat_id)
    book = profile.last_book
    return book.id


def search_book(chat_id, text):
    profile = Profile.objects.get(tele_id=chat_id)
    user_id = profile.user.id
    objects = Book.objects.filter(
        (Q(title__icontains=text) |
         Q(title__in=text.split()) |
         Q(title__icontains=text.title()) |
         Q(title__in=text.title().split())) &
        Q(owner__pk=user_id)
    )
    result = objects.first()
    if result:
        set_last_book(profile, result)
    return result
