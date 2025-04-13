"""Engine bot"""
# Прописать больше информации в функциях (проименовать их в том числе), исправить групповой хендлер
# В private всё без о ш и б о к
# Потом уже Dockerfile, README.md, gitignore и залив на хост

import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator

from src.utils.config import settings
from src.handlers import router as main_router
from src.redis.engine import redis
from src.redis.requests import clear_all_db
from src.utils.middlewares import TranslateMiddleware, ThrottlingMiddleware

t_hub = TranslatorHub(
    {
        "ru": ("ru",),
        "en": ("en", "ru")
    },
    translators=[
        FluentTranslator(
            locale="ru",
            translator=FluentBundle.from_files(
                "ru-RU",
                filenames=[
                    "src/i18n/ru/text.ftl",
                    "src/i18n/ru/button.ftl"
                ]
            )
        ),
        FluentTranslator(
            locale="en",
            translator=FluentBundle.from_files(
                "en-US",
                filenames=[
                    "src/i18n/en/text.ftl",
                    "src/i18n/en/button.ftl"
                ]
            )
        )
    ],
    root_locale="ru",
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def main():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)) # подходит для .ftl файлов
    dp = Dispatcher(storage=RedisStorage(redis=redis), t_hub=t_hub)

    dp.include_router(main_router)

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(TranslateMiddleware())

    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(TranslateMiddleware())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except ValueError as e:
        logging.error("ValueError occurred: %s: ", e)
    except KeyError as e:
        logging.error("KeyError occurred: %s:", e)
    finally:
        await bot.session.close()
        await clear_all_db()


if __name__ == '__main__':
    try:
        logging.info('Бот запущен')
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Бот выключен')