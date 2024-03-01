from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from database.db import show_all_student_group

router = Router()


class Results(StatesGroup):
    group = State()


@router.message(Command(commands=['результаты']))
async def get_groups_list(message: Message, state:FSMContext):
    data = show_all_student_group()
    builder = InlineKeyboardBuilder()
    for group in data:
        builder.row(InlineKeyboardButton(text=group, callback_data=f'{data[group]}r'))
    await message.answer('Выбери группу для просмотра результатов', reply_markup=builder.as_markup())
    await state.set_state(Results.group)


@router.callback_query(F.data.contains)
async def show_all_data(callback:CallbackQuery, state:FSMContext):
    pass
