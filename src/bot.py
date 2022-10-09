from telebot.types import Message
from src.keys import keys_start, keys_menu
from src.adjustment import translit
from src.processing import bot, hello_user, preparing_search, add_id, remove_id
from src.history import get_history
from src.search import low_price, high_price, best_deal

@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    """
    `start` — это функция, которая выполняется при активации бота. Получает id пользователя и добавляет его в базу
    данных, представляющая собой json-файл data. В ответ на сообщение команда отправляет текст представление.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    chat_id: str = str(message.chat.id)
    add_id(chat_id)
    send_mess: str = (
        'Меня зовут Sonic Travel Bot.\n'
        'Я твой помощник по поиску отелей'
    )
    bot.send_message(message.from_user.id, text=send_mess, reply_markup=keys_start)

@bot.message_handler(commands=['hello_world'])
def hello_world(message: Message) -> None:
    """
    `hello_world` — это функция, которая обнуляет все данные пользователя и имитирует активацию бота.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    chat_id: str = str(message.chat.id)
    remove_id(chat_id)
    start(message)

@bot.message_handler(commands=['help'])
def helper(message: Message) -> None:
    """
    Функция отправляет сообщение пользователю со списком команд, доступных для работы с ботом.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    help_message: str = ('/hello_world - начать все сначала\n'
                         '/low_price - узнать топ самых дешёвых отелей в городе\n'
                         '/high_price - узнать топ самых дорогих отелей в городе\n'
                         '/best_deal - узнать топ отелей, наиболее подходящих по цене и расположению от центра '
                         '(самые дешёвые и находятся ближе всего к центру)\n'
                         '/history - узнать историю поиска отелей')
    bot.send_message(message.from_user.id, help_message, reply_markup=keys_menu)

@bot.message_handler(commands=['history'])
def history(message: Message):
    """
    Функция получает историю запросов пользователя из базы данных и отправляет ее пользователю

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    result: str = get_history(str(message.chat.id))
    if result is None:
        bot.send_message(message.from_user.id, 'Я пока не получал от тебя запросов')
    else:
        bot.send_message(message.from_user.id, 'И так, вот что ты уже искал(а):\n{}'.format(result))

@bot.message_handler(content_types=['text'])
def get_text_messages(message: Message) -> None:
    """
    Проверяет текст сообщения и вызывает соответствующую функцию. Если текст не соответствует ни одной команде,
    отправляется сообщение с фразой доктора Альфреда Лэннинга из фильма "Я - робот" и возможными сценариями дальнейшего
    взаимодействия.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    text_mess: str = translit(message.text.lower().strip())
    if 'привет' in text_mess:
        hello_user(message)
    elif text_mess == 'начать поиск':
        preparing_search(message)
    elif text_mess == 'топ дешевых отелей':
        low_price(message)
    elif text_mess == 'топ дорогих отелей':
        high_price(message)
    elif text_mess == 'лучшее совпадение':
        best_deal(message)
    elif text_mess == 'история поиска':
        history(message)
    elif text_mess == 'начать сначала':
        hello_world(message)
    else:
        bot.send_message(message.from_user.id, (
            'Извини, в ответах я ограничен - правильно задавай вопросы.\n'
            'Чтобы получить информацию о командах отправь /help\n'
            'Или выбери соответсвующий пункт меню'
        ), reply_markup=keys_menu)
