"""Message handlers for private chats"""

import logging

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from fluentogram import TranslatorRunner
from pydantic import ValidationError

from ....handlers.user.private.callback import handler_link_account
from ....parsers.account_info import search_account_by_nickname
from ....parsers.match_info import get_general_info_about_match
from ....parsers.info import get_info_about_account
from ....database.requests import (
    check_language_user,
    record_transaction,
    register_user_in_profile_table,
)
from ....utils.formatted_output import format_button_result, format_general_match_info
from ....utils.keyboards import (
    get_inline_buttons,
    account_buttons,
    get_start_keyboard_page_2,
    get_start_keyboard_page_1,
)
from ....utils.schemas import MatchSchema, AccountSchema
from .other import process_account_id
from .states import Info, AnotherInfo

router: Router = Router()
router.message.filter(F.chat.type == "private")


@router.message(CommandStart())
async def show_main_menu(message: Message, state: FSMContext, locale: TranslatorRunner):
    language = await check_language_user(message.from_user.id)
    if language == "":
        await message.answer(
            text=locale.language.select(),
            reply_markup=await get_inline_buttons(
                btns={"select_ru": "Русский", "select_en": "English"}
            ),
        )
    else:
        await message.answer(
            text=locale.welcome(user=message.from_user.full_name),
            reply_markup=await get_start_keyboard_page_1(locale),
        )

    await state.clear()


@router.message(Info.account_id, F.text)
async def handler_get_account_id(
    message: Message, state: FSMContext, bot: Bot, locale: TranslatorRunner
):
    await process_account_id(message.text, message.chat.id, state, bot, locale)


@router.message(Info.match_id, F.text)
async def handler_get_match_id(
    message: Message, state: FSMContext, locale: TranslatorRunner
):
    try:
        match = int(message.text)
        match_id = MatchSchema(match_id=match)
        await state.update_data(match_id=match_id.match_id)
        await message.answer(
            locale.detected_match(match_id=match_id.match_id),
        )

        query = await get_general_info_about_match(match_id.match_id, locale)
        result = format_general_match_info(query, locale)

        await message.answer(
            result,
            reply_markup=await get_inline_buttons(
                btns={"get_info_about_players": locale.get_info_about_players()}
            ),
        )

        await state.update_data(number_pages_for_match=int(query["quantity_players"]))

    except ValidationError as e:
        await message.answer(locale.error_validation())
        logging.exception(
            f"Ошибка ValidationError в handler_get_match_id: {e}", exc_info=True
        )
        return

    except ValueError as e:
        await message.answer(f"{locale.incorrect_input()}. {e}")
        logging.exception(
            f"Ошибка ValueError в handler_get_match_id: {e}", exc_info=True
        )
        return

    except TelegramBadRequest as e:
        await message.answer(locale.error_sending())
        logging.exception(
            f"Ошибка TelegramBadRequest в handler_get_match_id: {e}", exc_info=True
        )
        return

    except Exception as e:
        await message.answer(locale.unexcpected_error())
        logging.exception(
            f"Ошибка Exception в handler_get_match_id: {e}", exc_info=True
        )
        return


@router.message(Info.nickname, F.text)
async def handler_get_account_nickanme(
    message: Message, state: FSMContext, locale: TranslatorRunner
):

    await message.answer(locale.starting_search())

    query = await search_account_by_nickname(message.text)

    result = format_button_result(query)
    await state.update_data(number_pages_for_accounts=len(result))
    await state.update_data(accounts_data=result)

    await message.answer(
        locale.found_accounts(), reply_markup=await account_buttons(0, result, locale)
    )


@router.message(AnotherInfo.account_id, F.text)
async def handler_check_account_id(
    message: Message, state: FSMContext, locale: TranslatorRunner
):
    await message.answer(locale.detected_account())
    try:
        account_id = AccountSchema(account_id=int(message.text))
        query = await get_info_about_account(account_id.account_id, locale)
        if query:
            await register_user_in_profile_table(
                message.from_user.id, account_id.account_id
            )
            await message.answer(
                locale.account_is_linken(),
                reply_markup=await get_inline_buttons(btns={"back": locale.back()}),
            )
            await state.clear()
    except ValidationError as e:
        await message.answer(locale.error_validation())
        logging.exception(
            "Ошибка ValidationError в handler_check_account_id: %e", e, exc_info=True
        )
        await handler_link_account(message, state, locale)
        raise e

    except Exception as e:
        await message.answer(
            locale.unexpected_error(),
            reply_markup=await get_inline_buttons(btns={"back": locale.back()}),
        )
        logging.error("Ошибка в handler_check_account_id: %e", e, exc_info=True)
        await state.clear()
        raise e


@router.message(F.successful_payment)
async def handler_process_succesful_payment(message: Message, bot: Bot):
    try:
        await message.answer(
            f"Спасибо за поддержку! Ваш платеж успешно обработан. ID транзакции: {message.successful_payment.telegram_payment_charge_id}\n",
            message_effect_id="5104841245755180586",
        )
        await record_transaction(
            tg_id=message.from_user.id,
            amount=1,
            transaction_id=message.successful_payment.telegram_payment_charge_id,
        )

    except Exception as e:
        await message.answer("Произошла ошибка, пожертвование возвращено.")
        await bot.refund_star_payment(
            message.from_user.id, message.successful_payment.telegram_payment_charge_id
        )
        logging.info("Ошибка при поддержке звёздами: %e", e, exc_info=True)
