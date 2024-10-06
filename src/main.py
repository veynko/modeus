import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from modeus import auth
import os


dp = Dispatcher()

@dp.message(CommandStart())
async def bot_start(message: types.Message):
    await message.answer("Hello")
    

@dp.message(Command("check"))
async def check(message: types.Message):
    try:
            words = message.text.split()[1:]
            if len(words) != 2:
                 await message.answer("Invalid message")
            username, password = words
            token = await auth.get_token(username, password)
            await message.answer(f"{token.id}\n{token.token}")
    except Exception as e:
        await message.answer("Ups, something went wrong")
        logger.debug(f"AHTUNG!!! {e.with_traceback()}")


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

