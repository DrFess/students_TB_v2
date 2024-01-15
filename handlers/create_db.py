from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import create_tables

router = Router()


@router.message(Command(commands=['create_db']))
async def create_db(message: Message):
    try:
        create_tables()
        await message.answer('База данных создана')
    except Exception as e:
        await message.answer(f'Что-то пошло не так {e}')
