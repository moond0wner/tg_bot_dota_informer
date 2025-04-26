"""Bot middlewares"""

import logging
from typing import Any, Awaitable, Callable, Dict

from fluentogram import TranslatorHub
from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from cachetools import TTLCache

from ..database.requests import check_language_user, set_user


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

caches = {"default": TTLCache(maxsize=10_000, ttl=0.1)}


class UserMiddleware(BaseMiddleware):
    """
    Проверяет находиться ли пользователь в базе данных, если нет то добавляет
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        await set_user(tg_id=event.from_user.id, name=event.from_user.username)

        return await handler(event, data)


class TranslateMiddleware(BaseMiddleware):
    """
    Fluentogram translation middleware
    """

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        language = await check_language_user(event.from_user.id) or "ru"

        hub: TranslatorHub = data.get("t_hub")

        data["locale"] = hub.get_translator_by_locale(language)

        logging.info(
            f"Для пользователя {event.from_user.id} установлен язык: {language}"
        )
        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):
    """Throttling middleware"""

    def __init__(self, time_limit: int = 1) -> None:  # Исправлено: __init__
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
        self,
        handler: Callable[
            [Any, Dict[str, Any]], Awaitable[Any]
        ],  
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        if not hasattr(event, "from_user") or event.from_user is None:
            return await handler(event, data)

        if event.from_user.id in self.limit:
            logging.info(f"Троттлинг активен для пользователя: {event.from_user.id}")
            return
        else:
            self.limit[event.from_user.id] = None
        return await handler(event, data)
