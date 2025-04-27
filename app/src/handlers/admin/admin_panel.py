import asyncio
import logging
from typing import List

from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Filter, Command

from .states import Broadcast
from ...utils.config import settings
from ...utils.keyboards import get_inline_buttons
from ...database.requests import get_users

router = Router()


class AdminProtect(Filter):
    def __init__(self):
        self.admins = settings.ADMINS

    async def __call__(self, message: Message):
        return message.from_user.id == self.admins # так как админ всего один, то и проверяю через равенство


@router.message(AdminProtect(), Command('help'))
async def _(message: Message):
    await message.answer("Команды для администратора: "
                         "\n/help \- список команд\."
                         "\n/sendall \- отправить всем пользователям бота сообщение\."
                         "\n/statistics \- статистика о пользователях\.")


@router.message(AdminProtect(), Command('sendall'))
async def _(message: Message, state: FSMContext):
    await message.answer("Отправьте сообщение которое хотите пользователям")
    await state.set_state(Broadcast.message)


@router.message(AdminProtect(), Broadcast.message)
async def _(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await message.answer(f'Ваш текст: \n"{message.text}"\n\nПодтверждаете отправку?',
                         reply_markup=await get_inline_buttons(btns={'confirm': 'Подтверждаю ✅',
                                                                     'cancel': 'Отменить ❌'}, ), parse_mode='')
    await state.set_state(Broadcast.confirm)


@router.callback_query(AdminProtect(), Broadcast.confirm, F.data == 'confirm')
async def _(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await callback.message.edit_text("Сообщение принято, начинаю рассылку\.\.\.💭")

    data = await state.get_data()
    text = data.get('message')
    users: List[int] = await get_users()

    total_users = len(users)
    successful_count = 0
    failed_count = 0
    for user_id in users:
        success = await send_message_to_user(bot, user_id, text)
        if success:
            successful_count += 1
        else:
            failed_count += 1

        await asyncio.sleep(0.05)

    await state.clear()

    await callback.message.answer(f"Рассылка завершена\. \nИз {total_users} пользователей сообщение отправлено: \nУспешно: {successful_count}\nПровально: {failed_count}")


@router.callback_query(AdminProtect(), Broadcast.confirm, F.data == 'cancel')
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Рассылка отменена.")
    await callback.message.edit_text("Рассылка отменена.")
    await state.clear()


@router.message(AdminProtect(), Command('statistics'))
async def get_statistics_bot(message: Message):
    table = await get_users()

    if not table:
        await message.answer("Не удалось получить статистику пользователей.")
        return

    user_count = len(table)
    top_five_users = [
        f"Имя: {element['user']}, кол\-во запросов: {element['number_of_requests']}\n"
        for element in table[:5] 
    ]
    text = f"Количество пользователей: {user_count}\nТоп 5 пользователей:\n{''.join(top_five_users)}"

    await message.answer(text)

async def send_message_to_user(bot: Bot, tg_id: int, message: str) -> bool:
    """Отправляет конкретному пользователю сообщение"""
    try:
        await bot.send_message(chat_id=tg_id, text=f'Вам было отправлено сообщение: \n\n{message}', parse_mode='HTML')
        return True
    except Exception as e:
        logging.error(f'Возникла ошибка при отправке рассылке сообщения пользователю {tg_id}: {e}')
        return False
