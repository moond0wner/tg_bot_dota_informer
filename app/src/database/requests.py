"""Request to Redis"""

from datetime import datetime
import logging
from typing import Dict, List

from sqlalchemy import BigInteger, select

from ..database.engine import async_session
from ..database.models import User, Transaction, Profile


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
        raise


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
        raise


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
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            user.number_of_requests += 1
            await session.commit()
    except Exception as e:
        logging.error("Ошибка в increment_user_request_count: %e", e, exc_info=True)
        raise


async def check_user_requests(tg_id: int) -> int:
    """Возвращает кол-во запросов пользователя"""
    try:
        async with async_session() as session:
            query = await session.scalar(select(User).where(User.tg_id == tg_id))
            return query.number_of_requests
    except Exception as e:
        logging.error("Ошибка в check_user_requests: %e", e, exc_info=True)
        raise


async def record_transaction(tg_id: int, amount: int, transaction_id: str):
    """Записывает транзакцию в БД"""
    try:
        async with async_session() as session:
            transaction = Transaction(
                tg_id=tg_id, amount=amount, transaction_id=transaction_id
            )
            session.add(transaction)
            session.commit()
    except Exception as e:
        logging.error("Ошибка в record_transaction: %e", e, exc_info=True)
        raise


async def get_first_date_usage_bot(tg_id: int) -> datetime:
    """Возвращает дату первого использования бота пользователем"""
    try:
        async with async_session() as session:
            query = await session.scalar(select(User).where(User.tg_id == tg_id))
            return query.created
    except Exception as e:
        logging.error("Ошибка в get_first_date_usage_bot: %e", e, exc_info=True)
        raise


async def get_last_date_usage_bot(tg_id: int) -> datetime:
    """Возвращает дату последнего использования бота пользователем"""
    try:
        async with async_session() as session:
            query = await session.scalar(select(User).where(User.tg_id == tg_id))
            return query.updated
    except Exception as e:
        logging.error("Ошибка в get_first_date_usage_bot: %e", e, exc_info=True)
        raise


async def check_user_in_profile_table(tg_id: int) -> bool:
    """Проверяет, находится ли пользователь в таблице "profiles" и возвращает булевое значение"""
    try:
        async with async_session() as session:
            user = await session.scalar(select(Profile).where(Profile.tg_id == tg_id))
            return True if user else False
    except Exception as e:
        logging.error("Ошибка в check_user_in_profile_table: %e", e, exc_info=True)
        raise


async def get_account_id_in_profile(tg_id: int) -> BigInteger:
    """Возвращает ID аккаунта пользователя из таблицы "profiles"."""
    try:
        async with async_session() as session:
            query = await session.scalar(select(Profile).where(Profile.tg_id == tg_id))
            return query.account_id
    except Exception as e:
        logging.error("Ошибка в get_account_id_in_profile: %e", e, exc_info=True)
        raise


async def register_user_in_profile_table(tg_id: int, account_id: int):
    """Записывает пользователя в таблицу "profiles"."""
    try:
        async with async_session() as session:
            user = await session.scalar(select(Profile).where(Profile.tg_id == tg_id))
            if not user:
                session.add(Profile(tg_id=tg_id, account_id=account_id))
                await session.commit()
                logging.info("Пользователь %s успешно зарегистрирован в таблице 'profiles'!", tg_id)
    except Exception as e:
        logging.error("Ошибка в register_user_in_profile_table: %s", e, exc_info=True)
        raise


async def unregister_user_in_profile_table(tg_id: int):
    """Удаляет полязователя с таблицы "profiles"."""
    try:
        async with async_session() as session:
            query = await session.scalar(select(Profile).where(Profile.tg_id == tg_id))
            await session.delete(query)
            await session.commit()
    except Exception as e:
        logging.error("Ошибка в unregister_user_in_profile_table: %s", e, exc_info=True)   
        raise e