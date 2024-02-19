from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import add_teacher, add_student_group, show_all_student_group, check_teacher, show_all_teachers, \
    delete_group, add_theme, show_all_themes, add_question, edit_student_group, edit_student_name, edit_student_surname, \
    edit_student_patronymic
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


class Question(StatesGroup):
    content = State()
    first_answer = State()
    second_answer = State()
    third_answer = State()
    fourth_answer = State()
    right_answer = State()
    theme_id = State()
    data_check = State()


class EditStudentInfo(StatesGroup):
    telegram_id = State()
    info_params = State()
    switch = State()


@router.message(Command(commands=['moderate']))
async def moderate_menu(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Добавить преподавателя', callback_data='teacher'))
    builder.row(InlineKeyboardButton(text='Добавить тему', callback_data='theme'))
    builder.row(InlineKeyboardButton(text='Добавить вопрос', callback_data='question'))
    builder.row(InlineKeyboardButton(text='Добавить группу', callback_data='group'))
    builder.row(InlineKeyboardButton(text='Показать все группы', callback_data='all_groups'))
    builder.row(InlineKeyboardButton(text='Показать список преподавателей', callback_data='all_teachers'))
    builder.row(InlineKeyboardButton(text='Показать список тем', callback_data='all_themes'))
    builder.row(InlineKeyboardButton(text='Редактировать данные студента', callback_data='edit_student_info'))
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


@router.callback_query(F.data == 'all_themes')
async def input_theme(callback: CallbackQuery):
    data = show_all_themes()
    message = data.keys()
    await callback.message.answer(f'{message}')


@router.callback_query(F.data == 'question')
async def add_question_content(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Question.content)
    await callback.message.answer('Отправь текст вопроса', reply_markup=back_button)


@router.message(Question.content)
async def add_first_answer(message: Message, state: FSMContext):
    await state.update_data(content=message.text)
    await state.set_state(Question.first_answer)
    await message.answer('Отправь первый вариант ответа', reply_markup=back_button)


@router.message(Question.first_answer)
async def add_second_answer(message: Message, state: FSMContext):
    await state.update_data(first_answer=message.text)
    await state.set_state(Question.second_answer)
    await message.answer('Отправь второй вариант ответа', reply_markup=back_button)


@router.message(Question.second_answer)
async def add_third_answer(message: Message, state: FSMContext):
    await state.update_data(second_answer=message.text)
    await state.set_state(Question.third_answer)
    await message.answer('Отправь третий вариант ответа', reply_markup=back_button)


@router.message(Question.third_answer)
async def add_fourth_answer(message: Message, state: FSMContext):
    await state.update_data(third_answer=message.text)
    await state.set_state(Question.fourth_answer)
    await message.answer('Отправь четвертый вариант ответа', reply_markup=back_button)


@router.message(Question.fourth_answer)
async def add_right_answer(message: Message, state: FSMContext):
    await state.update_data(fourth_answer=message.text)
    await state.set_state(Question.right_answer)
    await message.answer('Отправь номер правильного ответа', reply_markup=back_button)


@router.message(Question.right_answer)
async def add_theme_id(message: Message, state: FSMContext):
    await state.update_data(right_answer=message.text)
    await state.set_state(Question.theme_id)
    await message.answer('Отправь номер темы', reply_markup=back_button)


@router.message(Question.theme_id)
async def question_data_check(message: Message, state: FSMContext):
    await state.update_data(theme_id=message.text)
    await state.set_state(Question.data_check)
    data = await state.get_data()
    text = f'Вопрос: {data["content"]}\n' \
           f'Первый вариант: {data["first_answer"]}\n' \
           f'Второй вариант: {data["second_answer"]}\n' \
           f'Третий вариант: {data["third_answer"]}\n' \
           f'Четвёртый вариант: {data["fourth_answer"]}\n' \
           f'Номер правильного ответа: {data["right_answer"]}\n' \
           f'Номер темы вопроса: {data["theme_id"]}'
    await message.answer(text, reply_markup=adding_answer)


@router.message(Question.data_check)
async def add_question_data(message: Message, state: FSMContext):
    if message.text == 'Да, всё верно.':
        data = await state.get_data()
        add_question(
            content=data["content"],
            first_answer=data["first_answer"],
            second_answer=data["second_answer"],
            third_answer=data["third_answer"],
            fourth_answer=data["fourth_answer"],
            right_answer=data["right_answer"],
            theme_id=data["theme_id"]
        )
        await message.answer('Вопрос добавлен')
    elif message.text == 'Нет, не все данные верные.':
        await message.answer('Придётся начать всё заново')
    else:
        await message.answer('Что-то пошло не так', reply_markup=back_button)
    await state.clear()


@router.callback_query(F.data == 'edit_student_info')
async def get_student_telegram_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите telegramID студента')
    await state.set_state(EditStudentInfo.telegram_id)


@router.message(EditStudentInfo.telegram_id)
async def select_params_info(message: Message, state: FSMContext):
    await state.update_data(telegram_id=message.text)
    await state.set_state(EditStudentInfo.info_params)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='группу', callback_data='group_edit'))
    builder.row(InlineKeyboardButton(text='имя', callback_data='name_edit'))
    builder.row(InlineKeyboardButton(text='фамилию', callback_data='surname_edit'))
    builder.row(InlineKeyboardButton(text='отчество', callback_data='patronymic_edit'))
    await message.answer('Что изменить:', reply_markup=builder.as_markup())


@router.callback_query(EditStudentInfo.info_params, F.data.in_(
    {'group_edit', 'name_edit', 'surname_edit', 'patronymic_edit'}
))
async def get_new_info(callback: CallbackQuery, state: FSMContext):
    await state.update_data(switch=callback.data)
    await callback.message.answer(f'Пришлите на какое значение изменить {callback.message.text}')
    await state.set_state(EditStudentInfo.switch)


@router.message(EditStudentInfo.switch)
async def edit_student_info(message: Message, state: FSMContext):
    data = await state.get_data()
    if data.get('switch') == 'group':
        edit_student_group(data.get('telegram_id', int(message.text)))
        await message.answer('Группа изменена', reply_markup=back_button)
    elif data.get('switch') == 'name':
        edit_student_name('telegram_id', message.text)
        await message.answer('Имя изменено', reply_markup=back_button)
    elif data.get('switch') == 'surname':
        edit_student_surname('telegram_id', message.text)
        await message.answer('Фамилия изменена', reply_markup=back_button)
    elif data.get('switch') == 'patronymic':
        edit_student_patronymic('telegram_id', message.text)
        await message.answer('Отчество изменено', reply_markup=back_button)
    else:
        await message.answer('Что-то пошло не так', reply_markup=back_button)
    await state.clear()
