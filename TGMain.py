import asyncio
from app.DATA_Base import *
from aiogram import Bot, Dispatcher, F
from app.handerles import router
from config_data.config import Config, load_config


async def main():
    create_table()
    config: Config = load_config()
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')


