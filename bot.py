import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import check_teacher, check_student
from handlers import registration, moderation, create_db, geolocation
from keyboards import registration_kb
from settings import TOKEN

logging.basicConfig(level=logging.INFO, filename='log.log')

bot = Bot(token=TOKEN)
router = Router()

# test
@router.message(Command(commands=['start']))
async def start(message: Message):
    if check_teacher(message.from_user.id) or check_student(message.from_user.id):
        await message.answer(f'Привет, {message.from_user.username}')
    else:
        await message.answer('Я тебя не знаю, давай знакомиться?)', reply_markup=registration_kb)


@router.message(Command(commands=['menu']))
async def menu(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Отправить геолокацию', callback_data='geo'))
    await message.answer('Вы находитесь в главном меню', reply_markup=builder.as_markup())


@router.message(F.text == f'\U0001F519 Вернуться в меню')
async def menu(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Отправить геолокацию', callback_data='geo'))
    await message.answer('Вы находитесь в главном меню', reply_markup=builder.as_markup())


@router.message(Command(commands=['id']))
async def get_user_id(message: Message):
    await message.answer(f'Ваш telegramID: {message.from_user.id}')


async def main():
    dp = Dispatcher()
    dp.include_routers(
        router,
        registration.router,
        moderation.router,
        create_db.router,
        geolocation.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
