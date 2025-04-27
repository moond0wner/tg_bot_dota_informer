"""Callback handlers for private chats"""

import logging

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner

from ....database.requests import (
    check_language_user,
    save_user_language,
    increment_user_request_count,
)
from ....utils.keyboards import get_inline_buttons, start_buttons
from ....parsers.info import get_info_about_players_of_match
from .other import process_account_id, show_page, show_carousel
from .states import Info

router = Router()
router.message.filter(F.chat.type == "private")


@router.callback_query(F.data == "back")
async def show_main_menu(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):
    language = await check_language_user(callback.from_user.id)
    await callback.answer()
    if language == "":
        await callback.message.answer(
            text=locale.language.select(),
            reply_markup=await get_inline_buttons(
                btns={"select_ru": "Русский", "select_en": "English"}
            ),
        )
    else:
        await callback.message.answer(
            text=locale.welcome(user=callback.from_user.full_name),
            reply_markup=await start_buttons(locale),
        )
    await state.clear()


@router.callback_query(F.data == "change_language")
async def change_language(callback: CallbackQuery, locale: TranslatorRunner):
    await callback.answer()

    await callback.message.answer(
        text=locale.language.select(),
        reply_markup=await get_inline_buttons(
            btns={"select_ru": "Русский", "select_en": "English"}
        ),
    )


@router.callback_query(F.data.in_(["select_ru", "select_en"]))
async def select_language(callback: CallbackQuery):
    user_id = callback.from_user.id
    language = "en" if callback.data == "select_en" else "ru"

    await save_user_language(user_id, language)

    await callback.answer()
    await callback.message.answer(
        "Language selected\\!" if language == "en" else "Язык выбран успешно\\!",
        reply_markup=await get_inline_buttons(
            btns={
                "back": "Вернуться в меню" if language == "ru" else "Back to the menu"
            }
        ),
    )


@router.callback_query(F.data == "account_info")
async def handler_account_info(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):
    await callback.answer()
    await callback.message.answer(locale.send.id.account())

    await state.set_state(Info.account_id)
    await increment_user_request_count(callback.from_user.id)


@router.callback_query(F.data == "match_info")
async def handler_match_info(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):
    await callback.answer()
    await callback.message.answer(locale.send.id.match())

    await state.set_state(Info.match_id)
    await increment_user_request_count(callback.from_user.id)


@router.callback_query(F.data == "account_by_nick")
async def handler_account_by_nick(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):
    await callback.answer()
    await callback.message.answer(locale.send.nickname())

    await state.set_state(Info.nickname)
    await increment_user_request_count(callback.from_user.id)


@router.callback_query(F.data.startswith("account_id:"))
async def handler_account_id(
    callback: CallbackQuery, state: FSMContext, bot: Bot, locale: TranslatorRunner
):
    await callback.answer()

    await process_account_id(
        callback.data.split(":")[-1], callback.message.chat.id, state, bot, locale
    )


@router.callback_query(F.data == "get_info_about_players")
async def handler_get_info_about_players(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):
    match_data = await state.get_data()
    match_id = match_data.get("match_id")

    if match_id is None:
        await callback.answer(locale.match_not_found())
        return

    try:
        players_data = await get_info_about_players_of_match(match_id, locale)
        print(players_data)
        await state.update_data(players_data=players_data)

        if not players_data:
            await callback.answer(locale.no_information_about_players_of_match())
            return

        await show_page(callback, state, 0, locale)

    except Exception as e:
        logging.error(f"Ошибка handler_get_info_about_players: {e}", exc_info=True)
        await callback.answer(locale.error_getting_info_about_players())
        return


@router.callback_query(F.data.startswith("page:"))
async def process_pagination(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):

    page = int(callback.data.split(":")[1])
    await show_page(callback, state, page, locale)


@router.callback_query(F.data.startswith("carousel:"))
async def process_carousel(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):
    page = int(callback.data.split(":")[1])
    await show_carousel(callback, state, page, locale)
