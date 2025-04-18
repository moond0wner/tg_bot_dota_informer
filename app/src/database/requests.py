"""Request to Redis"""
import logging
from typing import List

from ..database.engine import async_session
from ..database.models import User

from sqlalchemy import select

async def set_user(tg_id: int, name: str) -> None:
    """Добавляет пользователя в БД, если его ещё там нет"""
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                session.add(User(tg_id=tg_id, name=name))
                await session.commit()
                logging.info(f'Пользователь {tg_id} успешно зарегистрирован!')
    except Exception as e:
        logging.error(f'Ошибка в set_user: {e}')
        raise e


async def get_users() -> List[User]:
    """Возвращает список пользователей из БД"""
    try:
       async with async_session() as session:
           users = await session.scalars(select(User))
           return [user.tg_id for user in users.all()]

    except Exception as e:
        logging.error(f"Ошибка в get_users: {e}")
        return []


async def save_user_language(tg_id: int, language: str)-> None:
    """Записывает выбранный пользователем язык в БД"""
    try:
        async with async_session() as session:
            query = await session.scalar(select(User).where(User.tg_id == tg_id))

            query.language = language
            await session.commit()

    except Exception as e:
        logging.error(f'Ошибка в select_user_language: {e}')
        raise e


async def check_language_user(tg_id: int) -> str:
    """Помогает middleware просмотреть какой язык использует пользователь"""
    try:
        async with async_session() as session:
            query = await session.scalar(select(User).where(User.tg_id == tg_id))
            if query:
                return query.language if query.language else ''
            else:
                return ''

    except Exception as e:
        logging.error(f'Ошибка в check_langauge_user: {e}')
        return '' # возвращаю пустую строку если произошла ошибка