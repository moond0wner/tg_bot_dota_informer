"""Helper functions for handlers"""
import logging
import json

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner
from pydantic import ValidationError

from ....utils.schemas import AccountSchema
from ....parsers.account_info import AccountInfo, get_info_about_account
from ....utils.formatted_output import format_account_info, format_player_info_in_match
from ....utils.keyboards import account_buttons, paginated_buttons, special_button_for_account


async def process_account_id(
            account_id: str,
            chat_id: int,
            state: FSMContext,
            bot: Bot,
            locale: TranslatorRunner):

    try:
        account_id = AccountSchema(account_id=int(account_id))
        logging.info(f'After: {account_id}, {type(account_id.account_id)}')
        await state.update_data(account_id=account_id.account_id)
        await bot.send_message(
            chat_id=chat_id,
            text=locale.detected_account(account_id=account_id.account_id))

        query: AccountInfo = await get_info_about_account(account_id.account_id, locale)
        if query is None:
            await bot.send_message(chat_id=chat_id, text=locale.query_none())
            return

        result = format_account_info(query, locale)

        if result.count('None') > 0:
            result += f'\n\n{locale.probably_account_hidden()}'

        await bot.send_photo(
            chat_id=chat_id,
            photo=query.avatar,
            caption=result,
            reply_markup=await special_button_for_account(query.profile_url, locale),
        )
        logging.info(f'Информация {account_id.account_id} успешно отправлена')
    except ValidationError as e:
        await bot.send_message(chat_id=chat_id, text=locale.error_validation())
        logging.exception(f"Ошибка ValidationError: {e}")
        return

    except ValueError as e:
        await bot.send_message(chat_id=chat_id, text=f"{locale.incorrect_input()} {e}")
        logging.exception(f"Ошибка ValueError: {e}")
        return

    except TelegramBadRequest as e:
        await bot.send_message(chat_id=chat_id, text=locale.error_sending())
        logging.exception(f"Ошибка TelegramBadRequest: {e}")
        return

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=locale.unexpected_error())
        logging.exception(f"Ошибка Exception: {e}")
        return


async def show_carousel(callback: CallbackQuery,
                        state: FSMContext,
                        page: int,
                        locale: TranslatorRunner):
    data = await state.get_data()
    accounts = data.get('accounts_data')
    if accounts is None:
        await callback.answer("Нет данных о аккаунтах.")
        return


    keyboard = await account_buttons(page, accounts, locale)

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=keyboard)


async def show_page(callback: CallbackQuery,
                    state: FSMContext,
                    page: int,
                    locale: TranslatorRunner):
    """Функция для отображения страницы с пагинацией."""

    data = await state.get_data()
    players_data = data.get('players_data')
    number_pages = data.get('number_pages_for_match', 1)


    if players_data is None:
        logging.error("Данные о игроках отсутствуют.")
        await callback.answer(locale.no_players_found())
        return

    try:
        text = format_player_info_in_match(json.loads(players_data), page, locale)
    except Exception as e:
        logging.exception(f"Произошла ошибка при отображении страницы: {e}")
        await callback.answer(locale.error_sending())
        return

    keyboard = await paginated_buttons(page, number_pages, locale)
    try:
        await callback.message.edit_text(text, reply_markup=keyboard)

    except TelegramBadRequest as e:
        logging.warning(f"TelegramBadRequest при редактировании сообщения: {e}")
        await callback.message.answer(locale.unexpected_error(), reply_markup=keyboard)
        return

    except Exception as e:
        logging.exception(f"Произошла ошибка при отображении страницы: {e}")
        await callback.answer(locale.error_sending())
        return

    await callback.answer()



