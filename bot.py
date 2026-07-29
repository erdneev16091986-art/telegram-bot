import asyncio
import logging
import os
import random

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession
from fake_useragent import UserAgent

# ─── Конфигурация ──────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8533823661:AAGXp-807bssYualCB_AiWEk_YytpjrSEGY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()

# Соответствие названий городов slug-ам Avito (часть URL пути)
CITY_SLUGS = {
    "москва": "moskva",
    "мск": "moskva",
    "санкт-петербург": "sankt-peterburg",
    "спб": "sankt-peterburg",
    "питер": "sankt-peterburg",
    "казань": "kazan",
    "екатеринбург": "ekaterinburg",
    "новосибирск": "novosibirsk",
    "нижний": "nizhniy-novgorod",
    "ростов": "rostov-na-donu",
    "самара": "samara",
    "уфа": "ufa",
    "краснодар": "krasnodar",
    "владивосток": "vladivostok",
    "сочи": "sochi",
    "пермь": "perm",
}

# Генератор случайных User-Agent
ua = UserAgent()


# ─── Вспомогательные функции ───────────────────────────────────────
def get_headers() -> dict:
    """Случайные заголовки для HTTP-запроса."""
    return {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def build_url(city: str, price: int) -> str:
    """Собирает URL поиска квартир на Avito по городу и макс. цене."""
    slug = CITY_SLUGS.get(city.lower(), city.lower())
    return f"https://www.avito.ru/{slug}/kvartiry/prodam?price={price}"


def parse_page(html: str) -> list[dict]:
    """Извлекает 5 первых объявлений из HTML-страницы Avito."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", attrs={"data-marker": "item"})
    results = []

    for card in cards[:5]:
        link = card.find("a", attrs={"data-marker": "item-title"})
        if not link:
            continue
        href = link.get("href", "")
        full_url = f"https://www.avito.ru{href}" if href.startswith("/") else href

        title_tag = link.find("h3")
        title = title_tag.get_text(strip=True) if title_tag else "Без названия"

        price_meta = card.find("meta", attrs={"itemprop": "price"})
        price = price_meta["content"] if price_meta else "—"

        addr = card.find("div", attrs={"data-marker": "item-address"})
        address = addr.get_text(strip=True).replace("\u00a0", " ") if addr else ""

        results.append({"title": title, "price": price, "address": address, "url": full_url})

    return results


async def fetch_page(url: str) -> list[dict]:
    """
    Запрашивает страницу Avito с обходом Cloudflare (curl_cffi).
    - до 3 повторных попыток при ошибках
    - случайная задержка 3–7 секунд между попытками
    """
    last_error = None
    for attempt in range(1, 4):
        try:
            delay = random.uniform(3, 7)
            logger.info("Попытка %d/3, задержка %.1f с — %s", attempt, delay, url)
            await asyncio.sleep(delay)

            headers = get_headers()
            async with AsyncSession() as session:
                resp = await session.get(url, headers=headers, impersonate="chrome")
                resp.raise_for_status()
                return parse_page(resp.text)

        except Exception as exc:
            last_error = exc
            logger.warning("Ошибка попытки %d: %s", attempt, exc)

    logger.error("Все 3 попытки исчерпаны: %s", last_error)
    return []


# ─── Обработчики команд ────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n""Используй /search <город> <цена> для поиска квартир на Avito.\n"
        "Пример: /search москва 50000"
    )


@dp.message(Command("search"))
async def cmd_search(message: Message) -> None:
    """Команда /search <город> <цена> — парсит Avito и отдаёт 5 свежих ссылок."""
    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "❌ Формат: /search <город> <цена>\n"
            "Например: /search москва 50000"
        )
        return

    _, city, price_raw = parts

    try:
        price = int(price_raw)
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Цена должна быть целым положительным числом.")
        return

    status = await message.answer(f"🔍 Ищу квартиры в г. {city.lower()} до {price:,} ₽...")

    url = build_url(city, price)
    listings = await fetch_page(url)

    if not listings:
        await status.edit_text(
            f"😕 Ничего не найдено в г. {city.lower()} до {price:,} ₽.\n"
            "Попробуйте другие параметры."
        )
        return

    lines = [f"🏠 <b>Квартиры до {price:,} ₽, г. {city.title()}:</b>\n"]
    for i, item in enumerate(listings, 1):
        lines.append(
            f"{i}. <b>{item['title']}</b>\n"
            f"   💰 {item['price']} ₽\n"
            f"   📍 {item['address']}\n"
            f"   🔗 <a href=\"{item['url']}\">Смотреть</a>\n"
        )

    await status.edit_text("\n".join(lines), disable_web_page_preview=True, parse_mode="HTML")


# ─── Запуск бота ───────────────────────────────────────────────────
async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
