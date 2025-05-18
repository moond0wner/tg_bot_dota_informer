"""Callback handlers for private chats"""

from ast import Call
import logging

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, PreCheckoutQuery, LabeledPrice
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner
from ....database.requests import (
    check_language_user,
    save_user_language,
    increment_user_request_count,
    check_user_requests,
    get_first_date_usage_bot,
    get_last_date_usage_bot,
    check_user_in_profile_table,
    get_account_id_in_profile,
    unregister_user_in_profile_table
)
from ....utils.keyboards import (
    get_inline_buttons,
    get_start_keyboard_page_1,
    get_start_keyboard_page_2,
)
from ....parsers.info import get_info_about_players_of_match
from .other import process_account_id, show_page, show_carousel
from .states import Info, AnotherInfo

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
            reply_markup=await get_start_keyboard_page_1(locale),
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
        await state.update_data(players_data=players_data)

        if not players_data:
            await callback.answer(locale.no_information_about_players_of_match())
            return

        await show_page(callback, state, 0, locale)

    except Exception as e:
        logging.error(f"Ошибка handler_get_info_about_players: {e}", exc_info=True)
        await callback.answer(locale.error_getting_info_about_players())
        return


@router.callback_query(F.data == "support_project")
async def handler_support_project(callback: CallbackQuery, locale: TranslatorRunner):
    await callback.answer()
    prices = [LabeledPrice(label="XTR", amount=1)]
    await callback.message.answer_invoice(
        title=locale.support_star(),
        description=locale.description_donate(),
        prices=prices,
        provider_token="",
        payload="support_project",
        currency="XTR",
    )


@router.pre_checkout_query()
async def handler_pre_checkout_(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@router.callback_query(F.data.startswith("account_id:"))
async def handler_account_id(
    callback: CallbackQuery, state: FSMContext, bot: Bot, locale: TranslatorRunner
):
    await callback.answer()

    await process_account_id(
        callback.data.split(":")[-1], callback.message.chat.id, state, bot, locale
    )


@router.callback_query(F.data == "user_profile")
async def handler_user_profile(
    callback: CallbackQuery, locale: TranslatorRunner, bot: Bot
):
    await callback.answer()

    user_in_table = await check_user_in_profile_table(callback.from_user.id)
    count_user_requests = await check_user_requests(callback.from_user.id)
    first_request = await get_first_date_usage_bot(callback.from_user.id)
    last_request = await get_last_date_usage_bot(callback.from_user.id)

    text = (
        f"{locale.name()} {callback.from_user.full_name}\n"
        f"{locale.user_requests()} {count_user_requests}\n"
        f"{locale.date_registration()} {first_request}\n"
        f"{locale.last_request()} {last_request}\n\n"
        f"{locale.account_is_not_linken() if not user_in_table else locale.account_is_linken()}"
    )

    user_photos = await bot.get_user_profile_photos(callback.from_user.id)
    user_avatar = user_photos.photos[0][-1].file_id

    if user_in_table:
        button = await get_inline_buttons(
            btns={"check_account": locale.check_account(),
                  "unlink_account": locale.unlink_account()}
        )
    else:
        button = await get_inline_buttons(btns={"link_account": locale.link_account()})

    await bot.send_photo(
        chat_id=callback.message.chat.id,
        photo=user_avatar,
        caption=text,
        reply_markup=button,
        parse_mode="HTML",  # для избежания ошибки связанной с markdown
    )


@router.callback_query(F.data == "check_account")
async def handler_check_account(
    callback: CallbackQuery, state: FSMContext, bot: Bot, locale: TranslatorRunner
):
    await callback.answer()
    account_id = await get_account_id_in_profile(callback.from_user.id)
    await process_account_id(account_id, callback.message.chat.id, state, bot, locale)


@router.callback_query(F.data == "link_account")
async def handler_link_account(
    callback: CallbackQuery, state: FSMContext, locale: TranslatorRunner
):
    await callback.answer()
    await callback.message.answer(locale.send.id.account())
    await state.set_state(AnotherInfo.account_id)


@router.callback_query(F.data == "unlink_account")
async def handler_unlink_account(
    callback: CallbackQuery, locale: TranslatorRunner
):
    await callback.answer()
    await unregister_user_in_profile_table(callback.from_user.id)
    await callback.message.answer(locale.account_unlinken(), 
                                  reply_markup=await get_inline_buttons(btns={"back": locale.back()}))

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


@router.callback_query(F.data.startswith("start_page:"))
async def process_pagination(
    callback: CallbackQuery, locale: TranslatorRunner
):
    await callback.answer()
    page = int(callback.data.split(":")[1])
    match page:
        case 1:
            keyboard = await get_start_keyboard_page_1(locale)
        case 2:
            keyboard = await get_start_keyboard_page_2(locale)
    await callback.message.edit_reply_markup(reply_markup=keyboard) 
    
