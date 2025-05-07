from aiogram import Bot, Dispatcher, Router
import asyncio
import logging
from commands.handlers.handlers import router


bot = Bot(token='а я не покажу))))')
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())
