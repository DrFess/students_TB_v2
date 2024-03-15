import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message, PollAnswer, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from geopy import distance

from database.db import show_questions_on_theme, add_student_answer, get_student_answer_and_score, \
    check_answers_in_database, delete_answers, add_student_attending, show_all_questions
from keyboards import info_geolocation, start_test, next_question, test_result
from settings import LATITUDE, LONGITUDE

router = Router()


class Testing(StatesGroup):
    start = State()
    question = State()
    finish = State()
    geolocation = State()


@router.callback_query(F.data.in_({str(x) for x in range(1, len(show_all_questions()) + 1)}))
async def start_testing(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Testing.start)
    test_id = int(callback.data)
    student_answers = check_answers_in_database(callback.from_user.id, test_id)
    if len(student_answers) > 0:
        delete_answers(student_answers)
    test = show_questions_on_theme(test_id)
    await state.update_data(
        telegram_id=callback.from_user.id,
        test=test,
        date=callback.message.date.today().strftime('%d-%m-%Y'),
        count=0
    )
    await callback.message.answer('Тест загружен. Начать тест?', reply_markup=start_test)


@router.callback_query(F.data.in_('first_final_test'))
async def start_final_testing(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Testing.start)
    test = {}
    for num in range(1, 10):
        add_dict = show_questions_on_theme(f'{num}')
        for key in add_dict:
            test[key] = add_dict[key]
    await state.update_data(
        telegram_id=callback.from_user.id,
        test=test,
        date=callback.message.date.today().strftime('%d-%m-%Y'),
        count=0
    )
    await callback.message.answer('Тест загружен. Начать тест?', reply_markup=start_test)


@router.message(Testing.start, (F.text == 'Начать тест') | (F.text == 'Следующий вопрос'))
async def ask_question(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['count'] <= (len(data['test']) - 1):
        serial_numbers = list(data['test'].keys())

        question = data['test']
        serial_number = serial_numbers[data['count']]

        question_text = question[serial_number][0]
        options = [
            question[serial_number][1],
            question[serial_number][2],
            question[serial_number][3],
            question[serial_number][4]
        ]
        await message.answer_poll(
            question=question_text,
            options=options,
            is_anonymous=False,
            reply_markup=next_question
        )

        await state.update_data(
            theme_id=question[serial_number][6],
            correct_answer=question[serial_number][5],
            count=data['count'] + 1
        )

        await state.set_state(Testing.question)

    else:
        await message.answer('Вопросы по теме закончились', reply_markup=test_result)
        await state.set_state(Testing.finish)


@router.poll_answer(Testing.question)
async def answer_poll(answer: PollAnswer, state: FSMContext):
    await state.update_data(student_answer=answer.option_ids[0] + 1)
    info = await state.get_data()
    if info['student_answer'] == int(info['correct_answer']):
        data = (info['telegram_id'], info['theme_id'], f'{info["student_answer"]} +')
    else:
        data = (info['telegram_id'], info['theme_id'], f'{info["student_answer"]} -')
    add_student_answer(data)
    await state.set_state(Testing.start)


@router.message(Testing.finish, F.text == 'Покажи результат')
async def return_test_result(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Отправить геолокацию', callback_data='geo'))
    await message.answer(f'Чтобы узнать свой результат нажми:', reply_markup=builder.as_markup())
    await state.set_state(Testing.geolocation)


@router.callback_query(Testing.geolocation, F.data == 'geo')
async def send_geolocation(callback: CallbackQuery):
    await callback.message.answer('Начни транслировать свою геопозицию. Если геопозицию просто отправишь - не зачту\n'
                                  'Подсказать как это сделать?', reply_markup=info_geolocation)


@router.message(Testing.geolocation, F.text == 'Да, подскажи')
async def how_to_share_location(message: Message):
    await message.answer_photo(
        'AgACAgIAAxkBAAKpZGSHPsxt1DBKVNzzniN7_TYMzMFVAALgyTEbA4JBSHlVtBHkEZLMAQADAgADeQADLwQ',
        caption='Нажми на "скрепку" слева от поля ввода сообщения'
    )
    await message.answer_photo(
        'AgACAgIAAxkBAAKpbmSHQCVqo6OqAn1Y-sqIzUJhmlmkAALkyTEbA4JBSPlIiYqYcYcuAQADAgADeQADLwQ',
        caption='Иногда "скрепка" может быть справа от поля ввода'
    )
    await message.answer_photo(
        'AgACAgIAAxkBAAKpcGSHQHaZ7lZbo2V0hQUvMN572RP-AALhyTEbA4JBSJJ0stNuAAHIhwEAAwIAA3kAAy8E',
        caption='В открывшемся меню внизу нажми на "Геопозиция"'
    )
    await message.answer_photo(
        'AgACAgIAAxkBAAKpcmSHQNuy4_M2GtM19MckfssJOemyAALiyTEbA4JBSP8IVhjNbvLeAQADAgADeQADLwQ',
        caption='В следующем меню выбери "Транслировать геопозицию". Длительность трансляции можно выбрать любое'
    )
    await message.answer_photo(
        'AgACAgIAAxkBAAKpdGSHQX85OJ_zd-oX5toLYymNWY8PAALjyTEbA4JBSIjJavB8yW6ZAQADAgADeQADLwQ',
        caption='Когда бот ответит что трансляцию можно остановить, нажми на "крестик" в правом верхнем углу'
    )
    await message.answer(
        'Следуя этой инструкции попробуй транслировать геопозицию\n'
        'Чтобы перезапустить бота \nнажми ---> /start.',
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Testing.geolocation, F.location)
async def write_location(message: Message, state: FSMContext):
    if message.location.live_period:
        data = await state.get_data()
        theme_id = data['theme_id']
        answers_and_score = get_student_answer_and_score(message.from_user.id, theme_id)

        student_coordinate = (message.location.latitude, message.location.longitude)
        const_coordinate = (LATITUDE, LONGITUDE)
        geolocation = distance.distance(const_coordinate, student_coordinate).km
        add_student_attending(message.from_user.id, datetime.datetime.now().strftime('%d-%m-%Y'), geolocation)

        await message.answer(f'Ваш результат: {answers_and_score[0] * 100}%\n')
    else:
        await message.answer('Геолокация не получена')
    await state.clear()