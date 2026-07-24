import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

# Токен берётся из переменной окружения BOT_TOKEN.
# Если она не задана, используется значение по умолчанию (для быстрого теста).
BOT_TOKEN = os.getenv("BOT_TOKEN", "8533823661:AAERMSNs-4vjkcgmBlMlG7kizVtIE3XBroU")

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я эхо-бот. Напиши мне что угодно, и я отвечу."
    )


@dp.message(F.text)
async def handle_any_message(message: Message) -> None:
    await message.answer("Я тебя понял!")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
