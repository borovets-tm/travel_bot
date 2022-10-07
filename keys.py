from telebot.types import InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# Список всех клавиатурных кнопок.
hello: InlineKeyboardButton = InlineKeyboardButton(text='Привет')
go: InlineKeyboardButton = InlineKeyboardButton(text='Начать поиск')
low_price: InlineKeyboardButton = InlineKeyboardButton(text='Топ дешевых отелей')
high_price: InlineKeyboardButton = InlineKeyboardButton(text='Топ дорогих отелей')
best_deal: InlineKeyboardButton = InlineKeyboardButton(text='Лучшее совпадение')
history: InlineKeyboardButton = InlineKeyboardButton(text='История поиска')
hello_world: InlineKeyboardButton = InlineKeyboardButton(text='Начать сначала')
yes: InlineKeyboardButton = InlineKeyboardButton(text='Да')
no:  InlineKeyboardButton = InlineKeyboardButton(text='Нет')

# Клавиатура для стартового сообщения.
keys_start: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keys_start.row(hello)

# Клавиатура для приветственного сообщения.
keys_hello: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keys_hello.row(go)

# Клавиатура меню.
keys_menu: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keys_menu.row(low_price, high_price)
keys_menu.row(best_deal, history)
keys_menu.row(hello_world)

# Клавиатура Да/нет
keys_answer: ReplyKeyboardMarkup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keys_answer.row(yes, no)

# Пустая клавиатура
keys_space = ReplyKeyboardRemove()
