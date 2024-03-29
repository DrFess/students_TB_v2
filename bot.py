import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import check_teacher, check_student
from handlers import registration, moderation, create_db, geolocation, lessons, attending
from keyboards import registration_kb
from settings import TOKEN


bot = Bot(token=TOKEN)
router = Router()


@router.message(Command(commands=['start']))
async def start(message: Message):
    if check_teacher(message.from_user.id) or check_student(message.from_user.id):
        await message.answer(f'Привет, {message.from_user.username}')
    else:
        await message.answer('Я тебя не знаю, давай знакомиться?)', reply_markup=registration_kb)


@router.message(Command(commands=['menu']))
async def menu(message: Message, state: FSMContext):
    await message.answer('Вы находитесь в главном меню. Бот находится в стадии разработки и все функции пока'
                         ' не доступны. Ожидайте приглашения пройти тест')
    await state.clear()


@router.message(F.text == f'\U0001F519 Вернуться в меню')
async def menu(message: Message):
    await message.answer('Вы находитесь в главном меню. Бот находится в стадии разработки и все функции пока'
                         ' не доступны. Ожидайте приглашения пройти тест')


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
        lessons.router,
        geolocation.router,
        attending.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
