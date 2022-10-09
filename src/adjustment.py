from typing import Dict, List
from enchant import Dict
import enchant
from deep_translator import GoogleTranslator

# Создание объекта словаря.
eng_dict: Dict = enchant.Dict('en_US')


def translit(text: str) -> str:
    """
    Функция берет строку, разбивает ее на слова, проверяет, есть ли слово в словаре, если нет, то транслитерирует его,
    а затем объединяет слова обратно в строку.

    :param text: str - текст для транслитерации
    :type text: str
    :return: строка.
    """
    tran_dict: Dict = {'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ',
                       'p': 'з', '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р',
                       'j': 'о', 'k': 'л', 'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м',
                       'b': 'и', 'n': 'т', 'm': 'ь', ',': 'б', '.': 'ю', '`': 'ё'}

    new_word: List = []
    new_line: str = ''
    for word in text.split():
        if not eng_dict.check(word.strip(r'/.,!?"\'@#$%^&*-_=+`~:;|]{[}<>')):
            for ch in word:
                new_word += map(str.capitalize if ch.isupper() else str.lower, tran_dict.get(ch.lower(), ch))
            new_line += ''.join(new_word) + ' '
        else:
            new_line += word + ' '
        new_word.clear()
    return new_line.rstrip()

def translate(text: str,  language: str = 'en') -> str:
    """
    Функция берет название города на русском языке, транслитерирует его на латиницу, если пользователь использовал
    английскую раскладку клавиатуры, а затем переводит на английский.

    :param text: Название города для перевода.
    :type text: str
    :param language: язык перевода.
    :type language: str
    :return: Переведенное название города.
    """
    if language != 'ru':
        text = translit(text)
    translated = GoogleTranslator(source='auto', target=language).translate(text)
    return translated
