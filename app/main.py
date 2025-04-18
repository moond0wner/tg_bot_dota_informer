"""Engine bot"""
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator

from src.utils.config import settings
from src.handlers import router as main_router
from src.database.engine import start_db
from src.utils.middlewares import TranslateMiddleware, ThrottlingMiddleware, UserMiddleware

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
    dp = Dispatcher(t_hub=t_hub)

    dp.include_router(main_router)

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(TranslateMiddleware())
    dp.message.middleware(UserMiddleware())

    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(TranslateMiddleware())
    dp.callback_query(UserMiddleware())

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await start_db()
        await dp.start_polling(bot)
    except ValueError as e:
        logging.error("ValueError occurred: %s: ", e)
    except KeyError as e:
        logging.error("KeyError occurred: %s:", e)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        logging.info('Бот запущен')
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Бот выключен')