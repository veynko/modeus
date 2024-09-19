import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import os


dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


async def main():
    if not "TOKEN" in os.environ.keys():
        logger.critical("TOKEN is not declared in the environment variables")
        exit(1)

    bot = Bot(token=os.environ.get("TOKEN"))
    logger.info("Staring Bot")
    await dp.start_polling(bot)
    logger.info("Stoping Bot")

if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(os.environ.get("LOGLEVEL", logging.DEBUG))
    
    # loop = asyncio.get_event_loop()

    asyncio.run(main())

