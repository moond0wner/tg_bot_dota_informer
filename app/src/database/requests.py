"""Request to Redis"""

import logging
from typing import Dict, List

from sqlalchemy import select

from ..database.engine import async_session
from ..database.models import User


async def set_user(tg_id: int, name: str) -> None:
    """Добавляет пользователя в БД, если его ещё там нет"""
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                session.add(User(tg_id=tg_id, name=name))
                await session.commit()
                logging.info(f"Пользователь {tg_id} успешно зарегистрирован!")
    except Exception as e:
        logging.error(f"Ошибка в set_user: {e}", exc_info=True)
        raise e


async def get_users() -> List[Dict]:
    """Возвращает список пользователей из БД"""
    try:
        async with async_session() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            user_data = []
            for user in users:
                user_data.append(
                    {"user": user.name, "number_of_requests": user.number_of_requests}
                )
            return user_data
    except Exception as e:
        logging.error(f"Ошибка в get_users: {e}", exc_info=True)
        return []


async def save_user_language(tg_id: int, language: str) -> None:
    """Записывает выбранный пользователем язык в БД"""
    try:
        async with async_session() as session:
            query = await session.scalar(select(User).where(User.tg_id == tg_id))

            query.language = language
            await session.commit()

    except Exception as e:
        logging.error(f"Ошибка в select_user_language: {e}", exc_info=True)
        raise e


async def check_language_user(tg_id: int) -> str:
    """Помогает middleware просмотреть какой язык использует пользователь"""
    try:
        async with async_session() as session:
            query = await session.scalar(select(User).where(User.tg_id == tg_id))
            if query:
                return query.language if query.language else ""
            else:
                return ""

    except Exception as e:
        logging.error(f"Ошибка в check_langauge_user: {e}", exc_info=True)
        return ""  # возвращаю пустую строку если произошла ошибка


async def increment_user_request_count(tg_id: int):
    """Увеличивает кол-во запросов пользователя в бота на единицу"""
    try:
        async with async_session() as session:
            cart = await session.scalar(select(User).where(User.tg_id == tg_id))
            cart.number_of_requests += 1
            await session.commit()
    except Exception as e:
        logging.error(f"Ошибка в increment_user_request_count: {e}", exc_info=True)
        raise e
