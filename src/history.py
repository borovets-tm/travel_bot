import os
import json
from typing import Dict, Optional

data_base = os.path.join('src', 'data.json')

def get_data() -> Dict:
    """
    Функция открывает файл, читает данные и возвращает их.
    :return: Словарь
    """
    with open(data_base, 'r') as file:
        data: Dict = json.load(file)
    return data

def write_history(data: Dict) -> None:
    """
    Функция открывает файл с именем `data.json` в режиме записи, выгружает данные в файл и закрывает его.

    :param data: Данные для записи в файл.
    :type data: Dict
    """
    with open(data_base, 'w') as file:
        json.dump(data, file, indent=4)

def add_search(chat_id: str, date_input: str, commands: str, search: str) -> None:
    """
    > Добавить поиск в историю пользователя

    :param chat_id: str - идентификатор чата пользователя.
    :type chat_id: str
    :param date_input: Дата, когда пользователь ввел команду.
    :type date_input: str
    :param commands: Команда, которую ввел пользователь.
    :type commands: str
    :param search: поисковый запрос
    :type search: str
    """
    data: Dict = get_data()
    user_history = data[chat_id]['history']
    date_log: Dict = user_history.setdefault(date_input, dict())
    date_log.setdefault('commands', commands)
    date_log.setdefault('results', [])
    date_log['results'].append(search)
    write_history(data)

def get_history(chat_id: str) -> Optional[str]:
    """
    Возвращает строку с историей запросов пользователя/

    :param chat_id: str - идентификатор чата пользователя
    :type chat_id: str
    """
    data: Dict = get_data()
    user_history: Dict = data[chat_id].get('history')
    if user_history:
        info: str = 'История запросов:\n'
        for time_h, result in user_history.items():
            info += '{date} - {command}\n\n'.format(date=time_h, command=result.get('commands'))
            info += '\n\n'.join(result.get('results'))
            info += '\n' + '=' * 30 + '\n'
        return info
    return None
