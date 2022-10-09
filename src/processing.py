from telebot import TeleBot
import os
import configparser
from src.history import get_data, write_history
from src.adjustment import translit
from src.keys import keys_hello, keys_menu
from telebot.types import Message
from typing import Dict

settings = os.path.join('src', 'settings.ini')
config = configparser.ConfigParser()
config.read(settings)
token = config['BOT']['TOKEN']
bot = TeleBot(token)

def add_id(chat_id: str) -> None:
    """
    `add_id` добавляет новый идентификатор чата в файл данных, если он еще не существует

    :param chat_id: str - идентификатор чата пользователя
    :type chat_id: str
    """
    data: Dict = get_data()
    if chat_id not in data.keys():
        data[chat_id]: Dict = {}
        data[chat_id].setdefault('history', {})
    write_history(data)

def remove_id(chat_id: str) -> None:
    """
    Функция удаляет chat_id из файла истории.

    :param chat_id: Идентификатор чата, который нужно хотите удалить.
    :type chat_id: str
    """
    data: Dict = get_data()
    if chat_id in data.keys():
        data.pop(chat_id)
        write_history(data)

def send_hello(message: Message, name: str) -> None:
    """
    Функция отправляет пользователю сообщение приветственный текст и клавиатуру keys_hello.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    :param name: имя пользователя
    :type name: str
    """
    bot.send_message(
        message.from_user.id,
        'Привет, {name}!\nНажми кнопку "Начать поиск"'.format(name=name),
        reply_markup=keys_hello
    )

def hello_user(message: Message) -> None:
    """
    Если у пользователя есть имя, ему отправится приветственное сообщение, в противном случае функция спросит его имя.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    chat_id = str(message.chat.id)
    data: Dict = get_data()
    if data[chat_id].get('name', ''):
        send_hello(message, data[chat_id].get('name'))
    else:
        bot.send_message(message.from_user.id, 'Давай познакомимся! Напиши мне свое имя?')
        bot.register_next_step_handler(message, set_name)

def set_name(message: Message) -> None:
    """
    Функция получает имя пользователя и сохраняет его в словаре данных.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    chat_id = str(message.chat.id)
    data: Dict = get_data()
    data[chat_id]['name']: str = translit(message.text.capitalize())
    send_hello(message, data[chat_id].get('name'))
    write_history(data)

def preparing_search(message: Message):
    """
    Функция отправляет пользователю сообщение со списком вариантов поиска отелей.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    bot.send_message(
        message.from_user.id,
        (
            'Я могу показать:\n'
            'Топ самых дешёвых отелей в городе /low_price.\n'
            'Топ самых дорогих отелей в городе /high_price.\n'
            'Топ отелей, наиболее подходящих по цене и расположению от центра '
            '(самые дешёвые и находятся ближе всего к центру) /best_deal.'
        ),
        reply_markup=keys_menu
    )
