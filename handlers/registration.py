from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import check_student, show_all_student_group, add_student
from keyboards import registration_answer, registration_kb, back_button

router = Router()


class RegistrationSteps(StatesGroup):
    first = State()
    second = State()
    third = State()
    fourth = State()
    last = State()


@router.message(F.text == 'Регистрация')
async def registration_start(message: Message, state: FSMContext):
    if not check_student(message.from_user.id):
        await state.set_state(RegistrationSteps.first)
        groups_dict = show_all_student_group()
        builder = InlineKeyboardBuilder()
        for group in groups_dict:
            builder.row(InlineKeyboardButton(text=group, callback_data=f'{groups_dict[group]}'))
        await message.answer('Регистрация начата. Выбери свою группу', reply_markup=builder.as_markup())
    else:
        await message.answer('Пользователь с таким telegram ID уже есть в базе данных')


@router.callback_query(RegistrationSteps.first)
async def registration_surname(callback: CallbackQuery, state: FSMContext):
    await state.update_data(group_id=callback.data)
    await state.set_state(RegistrationSteps.second)
    await callback.message.answer('Теперь отправь мне свою фамилию')


@router.message(RegistrationSteps.second)
async def registration_name(message: Message, state: FSMContext):
    await state.update_data(surname=message.text.capitalize())
    await state.set_state(RegistrationSteps.third)
    await message.answer('А теперь отправь своё имя.')


@router.message(RegistrationSteps.third)
async def registration_patronymic(message: Message, state: FSMContext):
    await state.update_data(name=message.text.capitalize())
    await state.set_state(RegistrationSteps.fourth)
    await message.answer('И последнее. Пришли мне своё отчество. Если его нет, просто отправь точку')


@router.message(RegistrationSteps.fourth)
async def registration_group(message: Message, state: FSMContext):
    await state.update_data(patronymic=message.text.capitalize())
    await state.set_state(RegistrationSteps.last)
    data = await state.get_data()
    await message.answer(
        f'Давай сверим информацию.\n'
        f'Твоя фамилия - {data["surname"]}\n'
        f'Твоё имя - {data["name"]}\n'
        f'Твоё отчество - {data["patronymic"]}\n'
        f'Всё правильно?',
        reply_markup=registration_answer
    )


@router.message(F.text == 'Да, всё верно. Закончить регистрацию', RegistrationSteps.last)
async def registration_end(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        add_student(
            telegram_id=message.from_user.id,
            surname=data['surname'],
            name=data['name'],
            patronymic=data['patronymic'],
            group_id=int(data['group_id'])
        )
        await message.answer('Регистрация успешна', reply_markup=back_button)
        await state.clear()
    except Exception as e:
        await message.answer(f'Произошла ошибка. Сообщите администратору. Текст ошибки: {e}')


@router.message(F.text == 'Нет, не все данные верные. Начать регистрацию заново', RegistrationSteps.last)
async def registration_again(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Хорошо, я Вас понял. Давайте начнём регистрацию заново', reply_markup=registration_kb)
