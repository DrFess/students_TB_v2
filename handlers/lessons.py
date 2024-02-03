import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot
from database.db import check_teacher, show_all_themes, show_all_student_group, show_theme_title, \
    show_student_group_title, show_group_students, add_lesson, show_teacher_id
from keyboards import back_button, adding_answer

router = Router()


class Lesson(StatesGroup):
    choose_group = State()
    theme_step = State()
    send_message = State()


@router.message(Command(commands=['занятие']))
async def group_selection(message: Message, state: FSMContext):
    if check_teacher(message.from_user.id):
        await state.set_state(Lesson.choose_group)
        builder = InlineKeyboardBuilder()
        groups_dict = show_all_student_group()
        for group in groups_dict:
            builder.row(InlineKeyboardButton(text=group, callback_data=f'{groups_dict[group]}'))
        await message.answer('Выбери группу у которой занятие', reply_markup=builder.as_markup())
    else:
        await message.answer('Нет доступа', reply_markup=back_button)


@router.callback_query(Lesson.choose_group)
async def theme_selection(callback: CallbackQuery, state: FSMContext):
    await state.update_data(group_id=callback.data)
    await state.set_state(Lesson.theme_step)
    builder = InlineKeyboardBuilder()
    themes_dict = show_all_themes()
    for theme in themes_dict:
        builder.row(InlineKeyboardButton(text=theme, callback_data=f'{themes_dict[theme]}'))
    await callback.message.answer('Выбери тему занятия', reply_markup=builder.as_markup())


@router.callback_query(Lesson.theme_step)
async def send_message_from_students(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    group_id = data['group_id']
    group = show_student_group_title(group_id)
    theme_id = callback.data
    theme = show_theme_title(theme_id)
    await state.update_data(theme_id=theme_id, group=group, theme=theme)
    await state.set_state(Lesson.send_message)
    await callback.message.answer(f'Отправить группе {group} тест по теме {theme}?', reply_markup=adding_answer)


@router.message(Lesson.send_message)
async def send_message_group(message: Message, state: FSMContext):
    if message.text == 'Да, всё верно.':
        teacher = show_teacher_id(message.from_user.id)
        data = await state.get_data()
        group_id = data['group_id']
        students = show_group_students(group_id)
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text=data['theme'], callback_data=data['theme_id']))
        for student in students:
            await bot.send_message(
                chat_id=student,
                text=f'Пройди тест по теме:',
                reply_markup=builder.as_markup()
            )
        add_lesson(
            datetime.datetime.now().strftime('%d-%m-%Y'),
            data['theme_id'],
            data['group'],
            teacher
        )
        await message.answer(f'Рассылка группе {data["group"]} отправлена', reply_markup=back_button)
    elif message.text == 'Нет, не все данные верные.':
        await message.answer('Рассылка не отправлена. Начни сначала', reply_markup=back_button)
    else:
        await message.answer('Что-то пошло не так', reply_markup=back_button)
    await state.clear()
