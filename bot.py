from aiogram import Bot, Dispatcher, Router
import asyncio
import logging
from commands.handlers.handlers import router


bot = Bot(token='7628523548:AAEDHYo_IMBsK4SSzHwKPVkNupwQ9KT0mz0')
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    asyncio.run(main())