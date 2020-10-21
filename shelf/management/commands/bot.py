import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from telegram import Bot, Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater
from telegram.utils.request import Request

import BookshelfBot.secrets
import shelf.management.commands.secrets
from shelf.management.commands.utils import num_to_words
from shelf.management.commands.voice_processing import recognize, synthesize
from shelf.models import Profile, Book


def log_errors(f):
    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_msg = f'Error occured: {e}'
            print(error_msg)
            raise e

    return inner


@log_errors
def answer(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    reply_text = 'error'

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
        try:
            print(text)
            result = search_book(chat_id, text)
            if result:
                bookcase = result.bookcase.title
                shelf = result.shelf.title
                row = result.shelf.row
                author = result.author.name
                reply_text = f'Книга - {result}, автор - {author}, шкаф: {bookcase}, {shelf}, {row} ряд'
            else:
                reply_text = f'По запросу "{text}" не найдено не одной книги в вашей библиотеке'
        except Exception as e:
            reply_text = (f'Для продолжения работы необходимо зарегистрироваться и создать базу данных.'
                          f' При регистрации укажите ваш telegram ID - {chat_id}')

    if is_voice:
        answer_path = os.path.join(settings.BASE_DIR, 'answer.ogg')
        synthesize(reply_text, answer_path)
        update.message.reply_voice(
            voice=(open(answer_path, 'rb'))
        )
    else:
        update.message.reply_text(
            text=reply_text
        )


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
    return result


class Command(BaseCommand):
    help = 'Telegram bot'

    def handle(self, *args, **options):
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=BookshelfBot.secrets.TOKEN,
            # base_url=settings.PROXY_URL,
        )

        updater = Updater(
            bot=bot,
            use_context=True,
        )

        message_handler_voice = MessageHandler(Filters.voice, answer)
        message_handler_text = MessageHandler(Filters.text, answer)
        updater.dispatcher.add_handler(message_handler_voice)
        updater.dispatcher.add_handler(message_handler_text)

        updater.start_polling()
        updater.idle()
