"""Handlers for group chat"""
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from fluentogram import TranslatorRunner

from ....parsers.account_info import get_info_about_account, AccountInfo
from ....utils.formatted_output import format_account_info
from ....utils.keyboards import get_inline_url_button

router = Router()
router.message.filter(F.chat.type == 'group')


@router.message(CommandStart())
async def start(message: Message,
                locale: TranslatorRunner):
    await message.reply(text=locale.welcome(user=message.from_user.full_name))


@router.message(Command('help'))
async def helping(message: Message,
               locale: TranslatorRunner):
    await message.reply(text=
    locale.help(
        github="[Github](https://github.com/moond0wner)",
        telegram="[Telegram](https://t.me/nevertoolate00)"
    )
    )



@router.message(Command('getaccount'))
async def get_account(message: Message,
                      bot: Bot,
                      locale: TranslatorRunner):
    logging.info(f'Пользователь {message.from_user.full_name} ({message.from_user.id}) запросил информацию об аккаунте: {message.text}')
    account_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else None  # Получаем account_id
    if account_id:
        await message.reply(text=locale.getaccount())  # Выводит описание команды
        query: AccountInfo = await get_info_about_account(account_id, locale)
        if query is None:
            await message.answer(locale.query_none())
            return

        answer = format_account_info(query, locale)

        if answer.count('None') > 0:
            answer += f'\n\n{locale.probably_account_hidden()}'


        await bot.send_photo(
            chat_id=message.chat.id,
            photo=query.avatar,
            caption=answer,
            reply_markup=await get_inline_url_button(text='Steam profile', url=query.profile_url),
        )

    else:
        await message.reply(text="Пожалуйста, укажите ID аккаунта после команды /getaccount")


@router.message(Command('getmatch'))
async def get_match(message: Message,
                    locale: TranslatorRunner):
    logging.info(
        f'Пользователь {message.from_user.full_name} ({message.from_user.id}) запросил информацию о матче: {message.text}')
    match_id = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else None
    if match_id:
        await message.reply(text=locale.getmatch())
        # Здесь код для получения и вывода информации о матче (заглушка)
        await message.reply(text=f"Информация о матче {match_id} (в разработке)")
    else:
        await message.reply(text="Пожалуйста, укажите ID матча после команды /getmatch")
