"""Inline/Reply/Paginated keyboards"""

import logging

from typing import Dict

from aiogram.types import (
    InlineKeyboardButton,
    KeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from fluentogram import TranslatorRunner

delete_kb = ReplyKeyboardRemove()


async def paginated_buttons(
    page: int, number_of_page: int, locale: TranslatorRunner
) -> InlineKeyboardMarkup:
    try:
        keyboard = InlineKeyboardBuilder()

        previous_page = page > 0
        next_page = page < number_of_page - 1

        navigation_buttons = []

        if previous_page:
            navigation_buttons.append(
                InlineKeyboardButton(text="<<", callback_data=f"page:{page - 1}")
            )

        if next_page:
            navigation_buttons.append(
                InlineKeyboardButton(text=">>", callback_data=f"page:{page + 1}")
            )

        if navigation_buttons:
            keyboard.row(*navigation_buttons)

        keyboard.row(
            InlineKeyboardButton(
                text=f"{page + 1}/{number_of_page}", callback_data="dummy_action"
            )
        )

        keyboard.row(InlineKeyboardButton(text=locale.back(), callback_data="back"))
        return keyboard.as_markup()

    except Exception as e:
        raise e


async def account_buttons(
    page: int, accounts: Dict[str, str], locale: TranslatorRunner
) -> InlineKeyboardMarkup:
    try:
        accounts = list(accounts.items())
        accounts_per_page = 5

        start_index = page * accounts_per_page
        end_index = start_index + accounts_per_page

        accounts_on_page = dict(accounts[start_index:end_index])
        number_of_pages = (len(accounts) + accounts_per_page - 1) // accounts_per_page

        keyboard = InlineKeyboardBuilder()
        for account_id, name in accounts_on_page.items():
            keyboard.row(
                InlineKeyboardButton(
                    text=name, callback_data=f"account_id:{account_id}"
                )
            )

        previous_page = page > 0
        next_page = end_index < len(accounts) - 1

        navigation_buttons = []

        if previous_page:
            navigation_buttons.append(
                InlineKeyboardButton(text="<<", callback_data=f"carousel:{page - 1}")
            )

        if next_page:
            navigation_buttons.append(
                InlineKeyboardButton(text=">>", callback_data=f"carousel:{page + 1}")
            )

        keyboard.row(
            InlineKeyboardButton(
                text=f"{page + 1}/{number_of_pages}", callback_data="dummy_action"
            )
        )

        if navigation_buttons:
            keyboard.row(*navigation_buttons)

        keyboard.row(InlineKeyboardButton(text=locale.back(), callback_data="back"))
        return keyboard.as_markup()
    except Exception as e:
        logging.exception(f"Ошибка при создании кнопок аккаунтов: {e}")
        raise e


async def get_inline_buttons(
    *, btns: dict[str, str], sizes: tuple[int] = (2,)
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for data, text in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


async def special_button_for_account(
    url: str, locale: TranslatorRunner
) -> InlineKeyboardMarkup:
    # Создаем клавиатуру
    keyboard = InlineKeyboardBuilder()

    steam_button = InlineKeyboardButton(text="Steam profile", url=url)

    back_button = InlineKeyboardButton(text=locale.back(), callback_data="back")

    keyboard.add(steam_button)
    keyboard.add(back_button)

    return keyboard.adjust(1).as_markup()


async def start_buttons(locale: TranslatorRunner):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=locale.get_info_about_account(), callback_data="account_info"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=locale.search_account_by_nickname(),
                    callback_data="account_by_nick",
                )
            ],
            [
                InlineKeyboardButton(
                    text=locale.get_info_about_match(), callback_data="match_info"
                )
            ],
            [InlineKeyboardButton(text="Language 💬", callback_data="change_language")],
            [
                InlineKeyboardButton(
                    text="Source code 👀",
                    url="https://github.com/moond0wner/tg_bot_dota_informer",
                )
            ],
        ]
    )
    return keyboard


async def get_reply_buttons(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )
