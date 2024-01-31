from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

back_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=f'\U0001F519 Вернуться в меню')]],
    one_time_keyboard=True,
    resize_keyboard=True
)

registration_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Регистрация')]],
    one_time_keyboard=True,
    resize_keyboard=True
)

registration_answer = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Да, всё верно. Закончить регистрацию')],
        [KeyboardButton(text='Нет, не все данные верные. Начать регистрацию заново')]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

adding_answer = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Да, всё верно.')],
        [KeyboardButton(text='Нет, не все данные верные.')]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

info_geolocation = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Да, подскажи')]
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)
