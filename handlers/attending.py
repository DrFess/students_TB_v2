from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import check_teacher, show_all_student_group, show_group_students
from keyboards import back_button

router = Router()


class AttendingResult(StatesGroup):
    choose_group = State()


@router.callback_query(F.data == 'attending_group_student')
async def choose_students_group(callback: CallbackQuery, state: FSMContext):
    if check_teacher(callback.from_user.id):
        await state.set_state(AttendingResult.choose_group)
        builder = InlineKeyboardBuilder()
        groups_dict = show_all_student_group()
        for group in groups_dict:
            builder.row(InlineKeyboardButton(text=group, callback_data=f'{groups_dict[group]}_attend'))
        await callback.message.answer('Выбери группу для которой сформировать посещения', reply_markup=builder.as_markup())
    else:
        await callback.message.answer('Нет доступа', reply_markup=back_button)


@router.callback_query(AttendingResult.choose_group, F.data.contains('_attend'))
async def testing(callback: CallbackQuery, state: FSMContext):
    group_id = callback.data.split('_')[0]
    students_telegram_id_in_group = show_group_students(group_id)
    await callback.message.answer(f'{students_telegram_id_in_group}')
    await state.clear()
