"""Message handlers for private chats"""

import logging

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from fluentogram import TranslatorRunner
from pydantic import ValidationError


from ....parsers.account_info import search_account_by_nickname
from ....parsers.match_info import get_general_info_about_match
from ....redis.requests import check_language_user
from ....utils.formatted_output import format_button_result, format_general_match_info
from ....utils.keyboards import get_inline_buttons, account_buttons
from ....utils.schemas import MatchSchema
from .other import process_account_id
from .states import Info

router: Router = Router()
router.message.filter(F.chat.type == "private")


@router.message(CommandStart())
async def show_main_menu(message: Message,
                         state: FSMContext,
                             locale: TranslatorRunner):
    language = await check_language_user(message.from_user.id)
    if language == '':
        await message.answer(
            text=locale.language.select(),
            reply_markup=await get_inline_buttons(
                btns={
                    'select_ru': 'Русский',
                    'select_en': 'English'
                }
            )
        )
    else:
        await message.answer(
            text=locale.welcome(user=message.from_user.full_name,
                                github='[Github](https://github.com/moond0wner/tg_bot_dota_informer)'),
            reply_markup=await get_inline_buttons(
                btns={
                    'account_info': locale.get_info_about_account(),
                    'account_by_nick': locale.search_account_by_nickname(),
                    'match_info': locale.get_info_about_match(),
                    'change_language': 'Language 💬'
                },
                sizes=(1,)
            )
        )

    await state.clear()


@router.message(Info.account_id, F.text)
async def _(message: Message,
            state: FSMContext,
            bot: Bot,
            locale: TranslatorRunner):
   await process_account_id(message.text, message.chat.id, state, bot, locale)



@router.message(Info.match_id, F.text)
async def _(message: Message,
            state: FSMContext,
            locale: TranslatorRunner):
    try:
        match = int(message.text)
        match_id = MatchSchema(match_id=match)
        await state.update_data(match_id=match_id.match_id)
        await message.answer(locale.detected_match(match_id=match_id.match_id),)

        query = await get_general_info_about_match(match_id.match_id, locale)
        result = format_general_match_info(query, locale)

        await message.answer(result,
        reply_markup=await get_inline_buttons(btns={"get_info_about_players": locale.get_info_about_players()}))

        await state.update_data(number_pages_for_match=int(query['quantity_players']))

    except ValidationError as e:
        await message.answer(locale.error_validation())
        logging.exception(f"Ошибка ValidationError: {e}")
        return

    except ValueError as e:
        await message.answer(f"{locale.incorrect_input()}. {e}")
        logging.exception(f"Ошибка ValueError: {e}")
        return

    except TelegramBadRequest as e:
        await message.answer(locale.error_sending())
        logging.exception(f"Ошибка TelegramBadRequest: {e}")
        return

    except Exception as e:
        await message.answer(locale.unexcpected_error())
        logging.exception(f"Ошибка Exception: {e}")
        return


@router.message(Info.nickname, F.text)
async def _(message: Message,
            state: FSMContext,
            locale: TranslatorRunner):

    await message.answer(locale.starting_search())

    query = await search_account_by_nickname(message.text)

    result = format_button_result(query)
    await state.update_data(number_pages_for_accounts=len(result))
    await state.update_data(accounts_data=result)

    await message.answer(locale.found_accounts(),
                         reply_markup=await account_buttons(0, result, locale))