"""Bot middlewares"""

import asyncio
import logging
import time
from typing import Any, Awaitable, Callable, Dict

from fluentogram import TranslatorHub
from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from cachetools import TTLCache

from ..redis.requests import check_language_user


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

caches = {
    "default": TTLCache(maxsize=10_000, ttl=0.1)
}


class TranslateMiddleware(BaseMiddleware):
    """
    Fluentogram translation middleware
    """

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        language = await check_language_user(event.from_user.id) or 'ru'

        hub: TranslatorHub = data.get('t_hub')

        data['locale'] = hub.get_translator_by_locale(language)

        logging.info(f'Для пользователя {event.from_user.id} установлен язык: {language}')
        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):  # pylint: disable=too-few-public-methods
    """
    Throttling middleware
    """

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        if not hasattr(event, "from_user") or event.from_user is None:
            return await handler(event, data)

        if event.from_user.id in caches["default"]:
            return
        caches["default"][event.from_user.id] = None
        return await handler(event, data)
