from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import add_teacher, add_student_group
from keyboards import adding_answer, back_button

router = Router()


class TeacherSteps(StatesGroup):
    first = State()
    second = State()
    third = State()
    fourth = State()
    end = State()


class GroupSteps(StatesGroup):
    first = State()


@router.message(Command(commands=['moderate']))
async def moderate_menu(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавить преподавателя', callback_data='teacher'))
    builder.row(InlineKeyboardButton(text='Добавить тему', callback_data='theme'))
    builder.row(InlineKeyboardButton(text='Добавить вопрос', callback_data='question'))
    builder.row(InlineKeyboardButton(text='Добавить группу', callback_data='group'))
    await message.answer('Включен режим модерирования', reply_markup=builder.as_markup())


@router.callback_query(F.data == 'teacher')
async def moderator_add_teacher_telegramID(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TeacherSteps.first)
    await callback.message.answer('Отправь telegram ID преподавателя')


@router.message(TeacherSteps.first)
async def moderator_add_teacher_surname(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.text)
    await state.set_state(TeacherSteps.second)
    await message.answer('Отправь фамилию преподавателя')


@router.message(TeacherSteps.second)
async def moderator_add_teacher_name(message: Message, state: FSMContext):
    await state.update_data(surname=message.text.capitalize())
    await state.set_state(TeacherSteps.third)
    await message.answer('Отправь имя преподавателя')


@router.message(TeacherSteps.third)
async def moderator_add_teacher_patronymic(message: Message, state: FSMContext):
    await state.update_data(name=message.text.capitalize())
    await state.set_state(TeacherSteps.fourth)
    await message.answer('Отправь отчество преподавателя')


@router.message(TeacherSteps.fourth)
async def moderator_check_teacher_info(message: Message, state: FSMContext):
    await state.update_data(patronymic=message.text.capitalize())
    await state.set_state(TeacherSteps.end)
    data = await state.get_data()
    await message.answer('Данные преподавателя:\n'
                         f'Telegram ID: {data["telegram_id"]}\n'
                         f'Фамилия: {data["surname"]}\n'
                         f'Имя: {data["name"]}\n'
                         f'Отчество: {data["patronymic"]}\n'
                         f'Верно?', reply_markup=adding_answer)


@router.message(TeacherSteps.end, F.text == 'Да, всё верно.')
async def moderator_add_teacher_info(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        add_teacher(
            telegram_id=data['telegram_id'],
            surname=data['surname'],
            name=data['name'],
            patronymic=data['patronymic']
        )
        await message.answer('Запись о преподавателе добавлена', reply_markup=back_button)
    except Exception as e:
        await message.answer(f'Что-то пошло не так: {e}')


@router.callback_query(F.data == 'group')
async def moderator_add_teacher_telegramID(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Отправь номер группы')
    await state.set_state(GroupSteps.first)


@router.message(GroupSteps.first)
async def add_new_group(message: Message, state: FSMContext):
    data = message.text.split(' ')
    try:
        add_student_group(data[0], data[1])
        await message.answer(f'Группа {message.text} добавлена', reply_markup=back_button)
    except Exception as e:
        await message.answer(f'Что-то пошло не так(( {e}', reply_markup=back_button)