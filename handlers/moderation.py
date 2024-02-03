from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import add_teacher, add_student_group, show_all_student_group, check_teacher, show_all_teachers, \
    delete_group, add_theme
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
    delete = State()


class ThemeSteps(StatesGroup):
    add = State()


@router.message(Command(commands=['moderate']))
async def moderate_menu(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавить преподавателя', callback_data='teacher'))
    builder.row(InlineKeyboardButton(text='Добавить тему', callback_data='theme'))
    builder.row(InlineKeyboardButton(text='Добавить вопрос', callback_data='question'))
    builder.row(InlineKeyboardButton(text='Добавить группу', callback_data='group'))
    builder.row(InlineKeyboardButton(text='Показать все группы', callback_data='all_groups'))
    builder.row(InlineKeyboardButton(text='Показать список преподавателей', callback_data='all_teachers'))
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
    await state.clear()


@router.callback_query(F.data == 'all_groups')
async def show_all_groups_in_message(callback: CallbackQuery):
    groups_dict = show_all_student_group()
    message = ''
    for group in groups_dict:
        message += f'{group}\n'
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Удалить группу', callback_data='delete_group'))
    await callback.message.answer(
        message,
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == 'delete_group')
async def select_group_for_delete(callback: CallbackQuery, state: FSMContext):
    if check_teacher(callback.from_user.id):
        await state.set_state(GroupSteps.delete)
        groups_dict = show_all_student_group()
        builder = InlineKeyboardBuilder()
        for group in groups_dict:
            builder.row(InlineKeyboardButton(text=group, callback_data=f'{groups_dict[group]}'))
        await callback.message.answer('Выбери группу для удаления', reply_markup=builder.as_markup())
    else:
        await callback.message.answer('Нет прав на удаление')


@router.callback_query(GroupSteps.delete)
async def delete_group_telegram(callback: CallbackQuery, state: FSMContext):
    data = int(callback.data)
    try:
        delete_group(data)
    except Exception as e:
        await callback.message.answer(f'{e}')
    finally:
        await state.clear()


@router.callback_query(F.data == 'all_teachers')
async def show_all_teachers_in_message(callback: CallbackQuery):
    data = show_all_teachers()
    message = data.values()
    await callback.message.answer(f'{message}')


@router.callback_query(F.data == 'theme')
async def input_theme(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Укажите название темы')
    await state.set_state(ThemeSteps.add)


@router.message(ThemeSteps.add)
async def add_theme_in_message(message: Message, state: FSMContext):
    try:
        add_theme(message.text)
        await message.answer(f'Тема "{message.text}" добавлена')
    except Exception as e:
        await message.answer(f'{e}')
    finally:
        await state.clear()

