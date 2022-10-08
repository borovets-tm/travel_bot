import requests
from datetime import datetime, date

from requests import Response

from adjustment import eng_dict, translate
from processing import bot
from history import add_search
from keys import keys_answer, keys_menu, keys_space
from telebot.types import Message
from typing import Dict, List, Callable, Tuple, Optional, Union

# Список команд, которые может обрабатывать бот.
commands = ['help', 'low_price', 'high_price', 'best_deal', 'start', 'hello_world', 'history']

def check_message(message: Message):
    """
    Если сообщение является командой, функция выполнит ее и вернет False, чтобы дальнейшие команды не выполнялись.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    :return: логическое значение.
    """
    if message.text.lstrip('/') in commands:
        if message.text.lstrip('/') == 'help':
            eval('helper')(message)
        else:
            eval(message.text.lstrip('/'))(message)
        return False
    return True

class GetInformation:
    """
    Этот класс отвечает за получение информации об отелях.
    :attr:
        __url_city: str - url API для поиска города.
        __url_data: str - url API для поиска отелей в городе.
        __url_photo: str - url API для получения фото отеля.
        __symbol: str - набор всех спецсимволов
        __headers: Dict - хранит в себе X-RapidAPI-Key и X-RapidAPI-Host для доступа к API
        __querystring: Dict - хранит в себе параметры запроса на получение данных об отелях в городе.
    """
    __url_city = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    __url_data = 'https://hotels4.p.rapidapi.com/properties/list'
    __url_photo = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
    __url_hotel = 'https://www.hotels.com/ho{}'
    __symbol = r' /.,!?"\'@#$%^&*-_=+`~:;|]{[}<>'
    __headers = {
        # 'X-RapidAPI-Key': '7a593b310amshc37cab9953ea291p13d79djsn71ab4b0bc312',
        'X-RapidAPI-Key': 'f5faadc275msh6e183e3048a08bcp19ae17jsnac19e10d9962',
        'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
    }
    __querystring = {
        'destinationId': '',
        'pageNumber': '1',
        'pageSize': '25',
        'checkIn': '',
        'checkOut': '',
        'adults1': '1',
        'sortOrder': '',
        'locale': 'en_US',
        'currency': 'USD'
    }

    def __init__(self, type_sort, command, date_time, landmark_ids=None):
        """
        Функция принимает тип_сортировки, команду, дату и время и ориентир в городе.

        Затем функция устанавливает type_sort в __querystring['sortOrder'], date_time в __date_log и command в
        __command.

        Если ориентир передается функцией, то функция устанавливает значение в landmarkIds и добавляет его к
        остальным параметрам.

        :param type_sort: Тип сортировки, который использует команда.
        :param command: Команда, которая выполняется.
        :param date_time: Дата и время начала операции.
        :param landmark_ids: Список идентификаторов ориентиров для сортировки результатов.
        """
        self.__querystring['sortOrder'] = type_sort
        self.__date_log = date_time
        self.__command = command
        if landmark_ids is not None:
            self.__querystring['landmarkIds'] = landmark_ids

    def get_city_id(self, message: Message):
        """
        Метод принимает сообщение от пользователя и проверяет, не является ли оно командой. Если это так, метод
        проверяет, написано ли сообщение на английском языке. Если это не так, он переводит сообщение на английский
        язык. Затем он отправляет запрос в API и получает ответ. Ответ представляет собой файл JSON.
        Затем функция анализирует файл JSON и получает идентификатор города. Если идентификатор города найден,
        функция отправляет пользователю сообщение с вопросом, сколько гостиниц он хочет посмотреть.
        Если идентификатор города не найден, функция отправляет пользователю сообщение о том, что город не найден.

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        """
        if check_message(message):
            __query: str = message.text.strip(self.__symbol)
            if not eng_dict.check(__query):
                __query: str = translate(__query)
            querystring: Dict = {'query': __query, 'locale': 'en_US', 'currency': 'USD'}
            response: Dict = requests.request('GET', self.__url_city, headers=self.__headers, params=querystring).json()
            data: List = response.get('suggestions')
            locality_info: List = data[0].get('entities')
            city: str = locality_info[0].get('destinationId')
            if city:
                self.__querystring['destinationId'] = city
                bot.send_message(
                    message.from_user.id,
                    'Я готов предложить до 25 результатов\nКакое количество отелей показать?',
                    reply_markup=keys_space
                )
                bot.register_next_step_handler(message, self.get_numbers_res)
            else:
                bot.send_message(
                    message.from_user.id,
                    'Я не нашел город {}\nПопробуй еще раз'.format(__query),
                    reply_markup=keys_space
                )
                bot.register_next_step_handler(message, self.get_numbers_res)

    def get_numbers_res(self, message: Message):
        """
        Метод принимает сообщение от пользователя и проверяет, не является ли оно командой. Если это так, то
        параметру pageSize присваивается значение текста сообщения, а если параметр pageSize
        является числом от 1 до 26, то пользователю предлагается ввести дату заезда в отель, в противном
        случае пользователю предлагается снова ввести количество результатов для отображения.

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        """
        if check_message(message):
            self.__querystring['pageSize']: str = message.text.strip(self.__symbol)
            if self.__querystring['pageSize'].isdigit() and 0 < int(self.__querystring['pageSize']) < 26:
                bot.send_message(
                    message.from_user.id,
                    'Когда заезжаем?\nПример: {date}'.format(date=datetime.today().strftime('%d.%m.%Y')),
                    reply_markup=keys_space
                )
                bot.register_next_step_handler(message, self.get_date_in)
            else:
                bot.send_message(
                    message.from_user.id,
                    'Укажи от 1 до 25 результатов!'
                )
                bot.register_next_step_handler(message, self.get_numbers_res)

    def check_date(self, message: Message, method: Callable, date_control: date) -> Optional[Tuple]:
        """
        Метод принимает сообщение и метод в качестве аргументов и возвращает кортеж из трех строк, если дата введена
        корректно или снова вызывает метод.

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        :param method: Callable — метод, который будет вызван, если дата неверна.
        :type method: Callable
        :param date_control: если вызывается метод get_date_out, то передается дата заезда, иначе значение отсутствует.
        :type date_control: date
        :return: Кортеж из трех строк.
        """
        error_mes = ''
        try:
            day, month, year = (int(num) for num in message.text.strip(self.__symbol).split('.'))
            date(year, month, day)
            if date(year, month, day) < date_control:
                raise TypeError
            if month < 10:
                month = '0' + str(month)
            if day < 10:
                day = '0' + str(day)
            return str(day), str(month), str(year)
        except ValueError:
            bot.send_message(
                message.from_user.id, 'Некорректная дата\nВведите дату, как в примере\nПример: {date}'.format(
                    date=datetime.today().strftime('%d.%m.%Y')
                ))
            return None
        except TypeError:
            if method == self.get_date_in:
                error_mes = 'Дата меньше текущей даты'
            elif method == self.get_date_out:
                error_mes = 'Дата меньше даты заезда'
            bot.send_message(
                message.from_user.id, '{error}\nВведите корректную дату\nПример: {date}'.format(
                    error=error_mes,
                    date=datetime.today().strftime('%d.%m.%Y')
                ))
            return None

    def get_date_in(self, message: Message):
        """
        Метод принимает сообщение, проверяет, является ли оно допустимой датой, и, если это так, устанавливает в
        параметр строки запроса checkIn дату в сообщении. После этого запрашивает у пользователя дату выезда.

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        """
        if check_message(message):
            date_today: date = datetime.today().date()
            date_in = self.check_date(message=message, method=self.get_date_in, date_control=date_today)
            if date_in is None:
                bot.register_next_step_handler(
                    message,
                    self.get_date_in
                )
            else:
                day, month, year = date_in
                self.__querystring['checkIn']: str = '-'.join((year, month, day))
                bot.send_message(
                    message.from_user.id,
                    'Теперь дата выезда\nПример: {date}'.format(date='{day}.{month}.{year}'.format(
                        day=int(day) + 10,
                        month=month,
                        year=year
                    ))
                )
                bot.register_next_step_handler(message, self.get_date_out)

    def get_date_out(self, message: Message):
        """
        Метод принимает сообщение, проверяет, является ли оно допустимой датой, и, если это так, устанавливает в
        параметр строки запроса checkOut дату в сообщении. После этого запрашивает у пользователя необходимость
        загрузки фотографий.

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        """
        if check_message(message):
            date_in: date = date.fromisoformat(self.__querystring['checkIn'])
            date_out = self.check_date(message=message, method=self.get_date_out, date_control=date_in)
            if date_out is None:
                bot.register_next_step_handler(
                    message,
                    self.get_date_out
                )
            else:
                day, month, year = date_out
                self.__querystring['checkOut']: str = '-'.join((year, month, day))
                bot.send_message(message.from_user.id, 'Загрузить фотографии?', reply_markup=keys_answer)
                bot.register_next_step_handler(message, self.get_photo)

    def get_photo(self, message: Message):
        """
        Если сообщение пользователя «да», то бот спрашивает, сколько фотографий пользователь хочет загрузить

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        """
        if check_message(message):
            if message.text.lower() == 'да':
                bot.send_message(message.from_user.id, 'Я могу предложить до 10 фото\nСколько фотографий загрузить?')
                bot.register_next_step_handler(message, self.get_count_photo)
            else:
                self.get_data(message)

    def get_count_photo(self, message: Message):
        """
        Если сообщение представляет собой число от 1 до 10, то вызывается функция get_data, в противном случае
        пользователю предлагается подтвердить количество фотографий

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        """
        if check_message(message):
            if message.text.isdigit() and 0 < int(message.text) < 11:
                self.get_data(message, int(message.text))
            else:
                bot.send_message(message.from_user.id, 'Так загружать или нет?', reply_markup=keys_answer)
                bot.register_next_step_handler(message, self.get_photo)

    def get_data(self, message: Message, num_photo: int = 0):
        """
        Метод принимает сообщение от пользователя, проверяет его, отправляет запрос на сервер, получает ответ,
        анализирует его и отправляет результат пользователю в виде списка сообщений, состоящих из данных об отелях
        и при необходимости фотографий. А так же передает данные для их сохранения в историю поиска пользователя.

        :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
        :type message: Message
        :param num_photo: int=0 - количество отправляемых фотографий, defaults to 0
        :type num_photo: int (optional)
        """
        if check_message(message):
            response: Response = requests.request(
                'GET',
                self.__url_data,
                headers=self.__headers,
                params=self.__querystring
            )
            data: List = response.json()['data']['body']['searchResults']['results']
            bot.send_message(message.chat.id, 'Вот что я нашел:', reply_markup=keys_menu)
            for hotel in data:
                name: str = hotel.get('name')
                url: str = self.__url_hotel.format(hotel.get('id'))
                add_dict: Dict = hotel.get('address')
                address = ' '.join((
                    add_dict.get('streetAddress'),
                    add_dict.get('locality'),
                    add_dict.get('postalCode'),
                    add_dict.get('region'),
                    add_dict.get('countryName')
                ))
                landmarks: Dict = hotel.get('landmarks')[0]
                to_centre: str = ' - '.join((landmarks.get('label'), landmarks.get('distance')))
                price_info: Dict = hotel.get('ratePlan').get('price')
                price: str = ' - '.join((price_info.get('info'), price_info.get('current'))).capitalize()
                total_price: str = price_info.get('fullyBundledPricePerStay').replace('&nbsp;', ' ').capitalize()
                querystring: Dict = {"id": str(hotel.get('id'))}
                result: List = [name, url, address, to_centre, price, total_price]
                info: str = '\n'.join(result)
                add_search(
                    chat_id=str(message.chat.id),
                    date_input=self.__date_log,
                    commands=self.__command,
                    search=info
                )
                bot.send_message(message.chat.id, info)
                if num_photo:
                    response: Dict = requests.request(
                        'GET', self.__url_photo, headers=self.__headers, params=querystring
                    ).json()
                    photos: List = response['hotelImages']
                    for score in range(num_photo):
                        url_photo: str = photos[score].get('baseUrl')
                        size: str = photos[score].get('sizes')[2].get('suffix')
                        photo: str = url_photo.format(size=size)
                        bot.send_photo(message.chat.id, requests.get(photo).content)


@bot.message_handler(commands=['low_price'])
def low_price(message: Message):
    """
    Функция, которая вызывается, когда пользователь нажимает кнопку «Топ дешевых отелей» или вводит команду /low_price.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    now: str = datetime.now().strftime('%d.%m.%Y - %H:%M:%S')
    type_sorted: str = 'PRICE'
    name: str = '/low_price'
    result = GetInformation(type_sort=type_sorted, command=name, date_time=now)
    bot.send_message(
        message.from_user.id,
        'Давай найдем топ самых доступных отелей!\nВ какой город отправимся?',
        reply_markup=keys_space
    )
    bot.register_next_step_handler(message, result.get_city_id)

@bot.message_handler(commands=['high_price'])
def high_price(message: Message):
    """
    Функция, которая вызывается, когда пользователь нажимает кнопку «Топ дорогих отелей» или вводит команду /high_price.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    now: str = datetime.now().strftime('%d.%m.%Y - %H:%M:%S')
    type_sorted: str = 'PRICE_HIGHEST_FIRST'
    name: str = '/high_price'
    result = GetInformation(type_sort=type_sorted, command=name, date_time=now)
    bot.send_message(
        message.from_user.id,
        'Давай найдем топ самых дорогих отелей!\nВ какой город отправимся?',
        reply_markup=keys_space
    )
    bot.register_next_step_handler(message, result.get_city_id)

@bot.message_handler(commands=['best_deal'])
def best_deal(message: Message):
    """
    Функция, которая вызывается, когда пользователь нажимает кнопку «Лучшее совпадение» или вводит команду /best_deal.

    :param message: объект, содержащий информацию о сообщении, отправленном пользователем.
    :type message: Message
    """
    now: str = datetime.now().strftime('%d.%m.%Y - %H:%M:%S')
    type_sorted: str = 'DISTANCE_FROM_LANDMARK'
    name: str = '/high_price'
    result = GetInformation(type_sort=type_sorted, command=name, landmark_ids='City center', date_time=now)
    bot.send_message(
        message.from_user.id,
        'Давай найдем лучшее сочетание по цене и удаленности от центра\nВ какой город отправимся?',
        reply_markup=keys_space
    )
    bot.register_next_step_handler(message, result.get_city_id)
