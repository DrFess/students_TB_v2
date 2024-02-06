import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, Message

from database.db import show_questions_on_theme
from keyboards import info_geolocation

router = Router()


class Testing(StatesGroup):
    start = State()


@router.callback_query(F.data.in_({'1', '2', '3', '4', '5', '6', '7', '8', '9'}))
async def testing(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Testing.start)
    test = show_questions_on_theme(callback.data)
    await callback.message.answer(f'{test}')


@router.callback_query(F.data == 'geo')
async def send_geolocation(callback: CallbackQuery):
    await callback.message.answer('Начни транслировать свою геопозицию. Если геопозицию просто отправишь - не зачту\n'
                                  'Подсказать как это сделать?', reply_markup=info_geolocation)


@router.message(F.text == 'Да, подскажи')
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


@router.message(F.location)
async def first_location(message: Message):
    if message.location.live_period:
        payload = {
            'longitude': message.location.longitude,
            'latitude': message.location.latitude,
            'telegram_id': message.from_user.id,
            'date': datetime.datetime.now().strftime('%Y-%m-%d')
        }
        await message.answer(f'{payload}')
    else:
        await message.answer('Геолокация не получена')
