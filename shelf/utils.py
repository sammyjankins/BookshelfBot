import requests
from PIL import Image
from bs4 import BeautifulSoup
from pyzbar.pyzbar import decode as p_decode

from shelf.models import Author, BookCase, Shelf, Book

URL = 'https://biblio.zone'

shelf_titles = {
    1: 'первая полка',
    2: 'вторая полка',
    3: 'третья полка',
    4: 'четвертая полка',
    5: 'пятая полка',
    6: 'шестая полка',
    7: 'седьмая полка',
    8: 'восьмая полка',
    9: 'девятая полка',
    10: 'десятая полка',
}
row_titles = {
    1: 'Первый',
    2: 'Второй',
    3: 'Третий',
    4: 'Четвертый',
}

sections_titles = {
    1: 'левая',
    2: 'правая',
}


def create_shelves(bookcase):
    for shelf_number in range(bookcase.shelf_count):
        for row_number in range(bookcase.row_count):
            for sections_number in range(bookcase.section_count):
                Shelf.objects.create(
                    title=f'{shelf_titles[shelf_number + 1]} {"слева" if sections_number + 1 == 1 else "справа"}',
                    row=row_titles[row_number + 1],
                    bookcase=bookcase,
                    owner=bookcase.owner)


def check_isbn_info(isbn):
    if not isbn:
        return None
    response = requests.get(f'{URL}/isbn/validator', params={'isbn': isbn})
    soup = BeautifulSoup(response.text, features="html.parser")
    success = soup.find('div', attrs={'data-res': 'success'})

    try:
        book_link = URL + success.find('a').attrs['href']
        book_response = requests.get(book_link)
        book_soup = BeautifulSoup(book_response.text, features="html.parser")

        table = book_soup.find('table').find_all('tr')
        table_data = {item[0].text[:-1]: item[1].text.strip() for item in [line.find_all('td') for line in table]}

        data_keys = {'Автор': 'author',
                     'ISBN': 'ISBN',
                     'Год издания': 'year_of_publication',
                     'Количество страниц': 'pages',
                     'Переплет': 'type_of_cover'
                     }

        book_data = {data_keys[key]: table_data[key] for key in data_keys if key in table_data}
        book_data.update({'title': book_soup.find('title').text,
                          'pages': ''.join([item for item in book_data['pages'] if item.isdigit()])})
        return book_data
    except Exception as e:
        return None


def get_author_of_create(author_name, user=None):
    authors = Author.objects.filter(owner__username=user.username)
    try:
        author = authors.get(name=author_name)
        print('got you - ', author)
        return author
    except Exception as e:
        print(e)
        author = Author(name=author_name, country='Country', date_of_birth='1999', owner=user)
        author.save()
        return author


def scan_isbn(img_file):
    barcode_pic = Image.open(img_file)
    decoded = p_decode(barcode_pic)
    try:
        return decoded[0].data.decode()
    except Exception as e:
        print(e)
        return None


def create_book(isbn, user, from_tg=False):
    book_data = check_isbn_info(isbn)
    if book_data is not None:
        author_name = book_data['author']
        author_object = get_author_of_create(author_name=author_name, user=user)
        bookcase = BookCase.objects.filter(owner__username=user).last()
        shelf = Shelf.objects.filter(owner__username=user).last()
        if not bookcase or not shelf:
            return None
        book_data.update({'author': author_object,
                          'bookcase': bookcase,
                          'shelf': shelf,
                          'owner': user, })
        book = Book(**book_data)
        book.save()
        return book
    else:
        return


class BookDataError(Exception):
    pass


class NoFurnitureError(Exception):
    pass
