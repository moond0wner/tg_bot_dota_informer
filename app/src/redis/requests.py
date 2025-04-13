"""Request to Redis"""

import logging

from ..redis.engine import redis

async def clear_all_db():
    await redis.flushdb()
    await redis.close()


async def save_user_language(user_id: int, language: str)-> None:
    """Записывает выбранный пользователем язык в БД"""
    try:
        await redis.set(name=f'Language for user {user_id}', value=language.encode('utf-8'), ex=86400)
    except Exception as e:
        logging.error(f'Ошибка в select_user_language: {e}')
        raise


async def check_language_user(user_id: int) -> str:
    """Помогает middleware просмотреть какой язык использует пользователь"""
    try:
        query = await redis.get(name=f'Language for user {user_id}')
        return query.decode('utf-8') if query else ''
    except Exception as e:
        logging.error(f'Ошибка в check_langauge_user: {e}')
        return '' # возвращаю пустую строку если произошла ошибка