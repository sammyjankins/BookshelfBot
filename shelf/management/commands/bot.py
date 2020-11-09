# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from telegram import Bot, Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater
from telegram.ext import CallbackQueryHandler
from telegram.utils.request import Request

from shelf.management.commands.utils import num_to_words, get_last_book, search_book, get_last_book_info
from shelf.management.commands.voice_processing import recognize, synthesize
from shelf.models import Profile
from shelf.utils import scan_isbn, create_book, BookDataError, NoFurnitureError

PROXY_URL = 'https://telegg.ru/orig/bot'

DIALOG_STATES = {
    0: 'initial',
    1: 'search',
    2: 'add',
}


# run this guy using:
# $ docker exec -it shelf bash
# $ python3 manage.py bot

def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_msg = f'Error occured: {e}'
            print(error_msg)
            raise e

    return inner


def set_dialog_state(profile, state):
    profile.state = state
    profile.save()


def get_profile_or_ask_register(chat_id):
    try:
        profile = Profile.objects.get(tele_id=chat_id)
        return profile
    except Exception as e:
        return None


@log_errors
def answer(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    reply_text = 'error'

    profile = get_profile_or_ask_register(chat_id)
    if profile:
        if profile.state == 0:
            reply_text = 'You can add a book to the library (to do this, you must have a bookcase in the database).'
            update.message.reply_text(
                text=reply_text,
                reply_markup=get_add_keyboard() if profile.last_book else get_nolastbook_keyboard(),
            )
        elif profile.state == 1:
            search_answer(profile, reply_text, update)
            set_dialog_state(profile, 0)
        elif profile.state == 2:
            add_book(chat_id, profile, update)
            set_dialog_state(profile, 0)
    else:
        reply_text = (f'Для продолжения работы необходимо зарегистрироваться и создать базу данных.'
                      f' При регистрации укажите ваш telegram ID - {chat_id}')
        update.message.reply_text(
            text=reply_text,
        )


def search_answer(profile, reply_text, update):
    try:
        file = update.message.voice.get_file()
        file_name = file.download()
        file_path = os.path.join(settings.BASE_DIR, file_name)
        text = recognize(file_path)['result']
        text = num_to_words(text)
        is_voice = True
    except Exception as e:
        text = update.message.text
        is_voice = False

    if text:
        result = search_book(profile, text)
        if result:
            bookcase = result.bookcase.title
            shelf = result.shelf.title
            row = result.shelf.row
            author = result.author.name
            reply_text = f'Книга - {result}, автор - {author}, шкаф: {bookcase}, {shelf}, {row} ряд'
        else:
            reply_text = f'По запросу "{text}" не найдено не одной книги в вашей библиотеке'

    if is_voice:
        answer_path = os.path.join(settings.BASE_DIR, 'answer.ogg')
        synthesize(reply_text, answer_path)
        update.message.reply_voice(
            voice=(open(answer_path, 'rb')),
            reply_markup=get_search_edit_info_keyboard(profile)
        )
    else:
        update.message.reply_text(
            text=reply_text,
            reply_markup=get_search_edit_info_keyboard(profile)
        )


def add_book(chat_id, profile, update):
    user = User.objects.get(profile__tele_id=chat_id)
    try:
        file = update.message.photo[-1].get_file()
        file_name = file.download()
        file_path = os.path.join(settings.BASE_DIR, file_name)
        text = scan_isbn(file_path)
        os.remove(file_path)
    except Exception as e:
        print(e)
        text = update.message.text
    if text:
        try:
            create_book(text, user)
            update.message.reply_text(
                text='The book profile was created successfully!\n'
                     f'Book info:\n{get_last_book_info(profile)}',
                reply_markup=get_search_edit_info_keyboard(profile),
            )
        except BookDataError as e:
            print(e)
            update.message.reply_text(
                text=f'No data found for the number {text}. Please fill out the form manually.',
                reply_markup=get_add_keyboard(),
            )
        except NoFurnitureError as e:
            print(e)
            update.message.reply_text(
                text=f'There are no bookcases or shelves in your profile. Please follow links'
                     f' in navbar to create bookcase so that you can fill it with books :)',
                reply_markup=get_add_keyboard()

            )
    else:
        update.message.reply_text(
            text='Error',
            reply_markup=get_add_keyboard()
        )


class Command(BaseCommand):
    help = 'Telegram bot'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=os.environ.get('TELEGRAM_TOKEN'),
            # base_url=PROXY_URL,
        )
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        message_handler_voice = MessageHandler(Filters.voice, answer)
        message_handler_photo = MessageHandler(Filters.photo, answer)
        message_handler_text = MessageHandler(Filters.text, answer)
        buttons_handler = CallbackQueryHandler(callback=keyboard_callback_handler, pass_chat_data=True)
        updater.dispatcher.add_handler(message_handler_voice)
        updater.dispatcher.add_handler(message_handler_photo)
        updater.dispatcher.add_handler(message_handler_text)
        updater.dispatcher.add_handler(buttons_handler)

        updater.start_polling()
        updater.idle()


# keyboard stuff =======================================================
# CB for Callback Button
CB_SEARCH = "callback_button_search"
CB_NEW_BOOK = "callback_button_new_book"
CB_NEW_BOOKCASE = "callback_button_new_bookcase"
CB_EDIT = "callback_button_edit"
CB_BOOK_INFO = "callback_button_book_info"

TITLES = {
    CB_SEARCH: "Найти книгу",
    CB_NEW_BOOK: "Добавить книгу",
    CB_NEW_BOOKCASE: "Добавить шкаф",
    CB_EDIT: "Редактировать",
    CB_BOOK_INFO: "Инфо",
}


def get_search_edit_info_keyboard(profile):
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CB_EDIT],
                                 # url=f'https://www.google.ru/',
                                 url=f'{os.environ.get("MY_CURRENT_URL")}shelves/book/{get_last_book(profile)}/edit/',
                                 callback_data=CB_EDIT),
            InlineKeyboardButton(TITLES[CB_BOOK_INFO], callback_data=CB_BOOK_INFO),
        ],
        [
            InlineKeyboardButton(TITLES[CB_SEARCH], callback_data=CB_SEARCH),
        ],

    ]
    return InlineKeyboardMarkup(keyboard)


def get_add_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CB_SEARCH], callback_data=CB_SEARCH),
        ],
        [
            InlineKeyboardButton(TITLES[CB_NEW_BOOK], callback_data=CB_NEW_BOOK),
            InlineKeyboardButton(TITLES[CB_NEW_BOOKCASE],
                                 url=f'{os.environ.get("MY_CURRENT_URL")}shelves/bookcase/create/',
                                 callback_data=CB_NEW_BOOKCASE),
        ],

    ]
    return InlineKeyboardMarkup(keyboard)


def get_nolastbook_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(TITLES[CB_NEW_BOOK], callback_data=CB_NEW_BOOK),
            InlineKeyboardButton(TITLES[CB_NEW_BOOKCASE],
                                 url=f'{os.environ.get("MY_CURRENT_URL")}shelves/bookcase/create/',
                                 callback_data=CB_NEW_BOOKCASE),
        ],

    ]
    return InlineKeyboardMarkup(keyboard)


def keyboard_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text
    profile = get_profile_or_ask_register(chat_id)
    if profile:

        if data == CB_NEW_BOOK:
            context.bot.send_message(
                chat_id=chat_id,
                text="I need the number or photo of the barcode on the back of the book.",
            )
            set_dialog_state(profile, 2)
        else:
            if profile.last_book is not None:
                if data == CB_SEARCH:
                    context.bot.send_message(
                        chat_id=chat_id,
                        text="What book should I look for?",
                    )
                    set_dialog_state(profile, 1)
                if data == CB_BOOK_INFO:
                    book_info = get_last_book_info(profile)
                    context.bot.send_message(
                        chat_id=chat_id,
                        text=book_info,
                        reply_markup=get_add_keyboard(),
                    )

            else:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="There are no books in your library, please add more books to use the bot.",
                    reply_markup=get_nolastbook_keyboard(),
                )

    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Для продолжения работы необходимо зарегистрироваться и создать базу данных.'
                 f' При регистрации укажите ваш telegram ID - {chat_id}',
        )
