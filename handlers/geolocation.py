from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data == 'geo')
async def send_geolocation(callback: CallbackQuery):
    await callback.message.answer('Эта функция пока в разработке')
