import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# БАЗА ДАННЫХ
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    metal TEXT,
    weight REAL,
    price REAL
)
""")

conn.commit()


# ГЛАВНОЕ МЕНЮ
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📄 Прайс-лист")],
        [KeyboardButton(text="⚖️ Расчёт стоимости металлолома")],
        [KeyboardButton(text="📏 Расчёт массы изделия")],
        [KeyboardButton(text="ℹ️ Информация о компании")],
        [KeyboardButton(text="🕘 История расчётов")]
    ],
    resize_keyboard=True
)


# START
@dp.message(CommandStart())
async def start(message: Message):
    text = (
        "👋 Приветствуем вас в РусЛом-Калькулятор!\n\n"
        "Я помогу вам узнать актуальные цены "
        "на металлолом, рассчитать стоимость "
        "и массу изделий, а также предоставлю "
        "справочную информацию о нашей компании.\n\n"
        "👇 Выберите нужный раздел:"
    )

    await message.answer(
        text,
        reply_markup=main_keyboard
    )


# ПРАЙС
@dp.message(F.text == "📄 Прайс-лист")
async def price_list(message: Message):

    text = (
        "💰 АКТУАЛЬНЫЙ ПРАЙС-ЛИСТ\n\n"

        "♻️ ЧЕРНЫЙ МЕТАЛЛ:\n"
        "🔩 3А — 21 500 ₽/т\n"
        "🔩 5А — 21 000 ₽/т\n"
        "🔩 Микс — 21 000 ₽/т\n"
        "🔩 12А — 21 000 ₽/т\n"
        "🔩 20А (чугун) — 21 000 ₽/т\n"
        "🔩 16А (стружка) — 12 000 ₽/т\n\n"

        "⚙️ ДОПОЛНИТЕЛЬНО:\n"
        "🔗 Проволока / трос до 7 мм — 10 000 ₽/т\n\n"

        "🚫 Не принимаются:\n"
        "❌ Амортизаторы\n"
        "❌ Газовые баллоны\n\n"

        "🟡 ЦВЕТНОЙ МЕТАЛЛ:\n"
        "⚪ Алюминий — 90 ₽/кг\n"
        "🚗 Алюм. радиаторы авто — 70 ₽/кг\n"
        "🔧 Нержавейка — 70 ₽/кг\n"
        "⚙️ Свинец — 80 ₽/кг\n"
        "🪙 ЦАМ — 50 ₽/кг\n"
        "🟡 Латунь — 250 ₽/кг\n"
        "🥉 Бронза — 250 ₽/кг\n"
        "🟠 Медь — 470 ₽/кг\n"
        "🔶 Медь лужёная — 300 ₽/кг\n"
        "♨️ Медные радиаторы — 350 ₽/кг\n"
        "📻 Радиаторы латунь — 220 ₽/кг\n"
        "🔋 Аккумуляторы — 50 ₽/кг\n\n"

        "📌 Цены могут изменяться."
    )

    await message.answer(text)

# РАСЧЕТ СТОИМОСТИ
@dp.message(F.text == "⚖️ Расчёт стоимости металлолома")
async def calc_price(message: Message):

    metal = "Медь"
    weight = 10
    price = 4700

    cursor.execute(
        "INSERT INTO history (user_id, metal, weight, price) VALUES (?, ?, ?, ?)",
        (message.from_user.id, metal, weight, price)
    )

    conn.commit()

    await message.answer(
        f"✅ Расчёт выполнен!\n\n"
        f"Металл: {metal}\n"
        f"Вес: {weight} кг\n"
        f"Стоимость: {price} ₽"
    )


# РАСЧЕТ МАССЫ
@dp.message(F.text == "📏 Расчёт массы изделия")
async def calc_weight(message: Message):
    await message.answer(
        "📏 Функция расчёта массы скоро будет доступна."
    )


# ИНФОРМАЦИЯ
@dp.message(F.text == "ℹ️ Информация о компании")
async def info(message: Message):
    await message.answer(
        "🏢 РусЛом37 — компания из города Иваново по приему и переработке металлолома."
    )


# ИСТОРИЯ
@dp.message(F.text == "🕘 История расчётов")
async def history(message: Message):

    cursor.execute(
        "SELECT metal, weight, price FROM history WHERE user_id=? ORDER BY id DESC LIMIT 5",
        (message.from_user.id,)
    )

    rows = cursor.fetchall()

    if not rows:
        await message.answer("📂 История расчётов пуста.")
        return

    text = "🕘 ИСТОРИЯ РАСЧЁТОВ\n\n"

    for row in rows:
        metal, weight, price = row

        text += (
            f"🔩 Металл: {metal}\n"
            f"⚖️ Вес: {weight} кг\n"
            f"💰 Стоимость: {price} ₽\n\n"
        )

    await message.answer(text)


# ЗАПУСК
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())