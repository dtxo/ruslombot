import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
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

# FSM СОСТОЯНИЯ
class CalcMetal(StatesGroup):
    metal = State()
    weight = State()


class CalcWeight(StatesGroup):
    length = State()
    width = State()
    thickness = State()


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

# НАЧАЛО РАСЧЕТА
@dp.message(F.text == "⚖️ Расчёт стоимости металлолома")
async def calc_price(message: Message, state: FSMContext):

    await state.set_state(CalcMetal.metal)

    await message.answer(
    "🔩 Введите тип металла:\n\n"

    "Доступные варианты:\n"
    "• алюминий\n"
    "• алюм. радиаторы авто\n"
    "• нержавейка\n"
    "• свинец\n"
    "• цам\n"
    "• латунь\n"
    "• бронза\n"
    "• медь\n"
    "• медь лужёная\n"
    "• медные радиаторы\n"
    "• радиаторы латунь\n"
    "• аккумуляторы"
    )


# ВВОД МЕТАЛЛА
@dp.message(CalcMetal.metal)
async def get_metal(message: Message, state: FSMContext):

    metal = message.text.lower().strip()

    # ЕСЛИ ЧЕЛОВЕК НАЖАЛ МЕНЮ
    if "история" in metal:
        await state.clear()
        return

    if "прайс" in metal:
        await state.clear()
        return

    if "информация" in metal:
        await state.clear()
        return

    if "массы" in metal:
        await state.clear()
        return

    prices = {
    "алюминий": 90,
    "алюм. радиаторы авто": 70,
    "нержавейка": 70,
    "свинец": 80,
    "цам": 50,
    "латунь": 250,
    "бронза": 250,
    "медь": 470,
    "медь лужёная": 300,
    "медные радиаторы": 350,
    "радиаторы латунь": 220,
    "аккумуляторы": 50
    }

    print(metal)
    print(prices.keys())

    if metal not in prices:
        await message.answer("❌ Такого металла нет в прайсе.")
        return

    await state.update_data(
        metal=metal,
        price_per_kg=prices[metal]
    )

    await state.set_state(CalcMetal.weight)

    await message.answer(
        "⚖️ Теперь введите вес в килограммах:"
    )


# ВВОД ВЕСА
@dp.message(CalcMetal.weight)
async def get_weight(message: Message, state: FSMContext):

    try:
        weight = float(message.text.replace(",", "."))

    except:
        await message.answer("❌ Введите число.")
        return

    data = await state.get_data()

    metal = data["metal"]
    price_per_kg = data["price_per_kg"]

    total = weight * price_per_kg

    # СОХРАНЕНИЕ В БАЗУ
    cursor.execute(
        "INSERT INTO history (user_id, metal, weight, price) VALUES (?, ?, ?, ?)",
        (
            message.from_user.id,
            metal,
            weight,
            total
        )
    )

    conn.commit()

    await message.answer(
        f"✅ РАСЧЁТ ГОТОВ\n\n"
        f"🔩 Металл: {metal.capitalize()}\n"
        f"⚖️ Вес: {weight} кг\n"
        f"💰 Цена за кг: {price_per_kg} ₽\n"
        f"💵 Итоговая стоимость: {total:.2f} ₽"
    )

    await state.clear()


# РАСЧЕТ МАССЫ ИЗДЕЛИЯ
@dp.message(F.text == "📏 Расчёт массы изделия")
async def calc_weight_start(message: Message, state: FSMContext):

    await state.set_state(CalcWeight.length)

    await message.answer(
        "📏 Введите длину листа в метрах:"
    )


# ДЛИНА
@dp.message(CalcWeight.length)
async def get_length(message: Message, state: FSMContext):

    try:
        length = float(message.text.replace(",", "."))

    except:
        await message.answer("❌ Введите число.")
        return

    await state.update_data(length=length)

    await state.set_state(CalcWeight.width)

    await message.answer(
        "📐 Введите ширину листа в метрах:"
    )


# ШИРИНА
@dp.message(CalcWeight.width)
async def get_width(message: Message, state: FSMContext):

    try:
        width = float(message.text.replace(",", "."))

    except:
        await message.answer("❌ Введите число.")
        return

    await state.update_data(width=width)

    await state.set_state(CalcWeight.thickness)

    await message.answer(
        "📎 Введите толщину листа в миллиметрах:"
    )


# ТОЛЩИНА
@dp.message(CalcWeight.thickness)
async def get_thickness(message: Message, state: FSMContext):

    try:
        thickness = float(message.text.replace(",", "."))

    except:
        await message.answer("❌ Введите число.")
        return

    data = await state.get_data()

    length = data["length"]
    width = data["width"]

    # перевод мм в метры
    thickness_m = thickness / 1000

    # плотность стали
    density = 7850

    # расчет массы
    weight = length * width * thickness_m * density

    await message.answer(
        f"✅ РАСЧЁТ МАССЫ ГОТОВ\n\n"
        f"📏 Длина: {length} м\n"
        f"📐 Ширина: {width} м\n"
        f"📎 Толщина: {thickness} мм\n\n"
        f"⚖️ Масса изделия: {weight:.2f} кг"
    )

    await state.clear()


# ИНФОРМАЦИЯ
@dp.message(F.text == "ℹ️ Информация о компании")
async def info(message: Message):
    await message.answer(
        "🏢 РусЛом37 — компания из города Иваново по приему и переработке металлолома."
    )


# ИСТОРИЯ РАСЧЁТОВ
@dp.message(F.text == "🕘 История расчётов")
async def history(message: Message):

    cursor.execute(
        "SELECT id, metal, price FROM history WHERE user_id=? ORDER BY id DESC LIMIT 10",
        (message.from_user.id,)
    )

    rows = cursor.fetchall()

    if not rows:
        await message.answer("📂 История расчётов пуста.")
        return

    text = "🕘 ИСТОРИЯ РАСЧЁТОВ\n\n"

    for i, row in enumerate(rows, start=1):

        calc_id, metal, price = row

        text += (
            f"{i}️⃣ {metal.capitalize()} — {price:.2f} ₽\n"
            f"ID расчёта: {calc_id}\n\n"
        )

    text += (
        "📌 Чтобы открыть расчёт,\n"
        "введите ID расчёта."
    )

    await message.answer(text)


# ЗАПУСК
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

# ОТКРЫТИЕ РАСЧЕТА ПО ID
@dp.message(F.text.regexp(r"^\d+$"))
async def open_history(message: Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state is not None:
        return

    calc_id = int(message.text)

    cursor.execute(
        "SELECT metal, weight, price FROM history WHERE id=?",
        (calc_id,)
    )

    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Расчёт не найден.")
        return

    metal, weight, price = row

    await message.answer(
        f"📂 ДЕТАЛИ РАСЧЁТА\n\n"
        f"🔩 Металл: {metal.capitalize()}\n"
        f"⚖️ Вес: {weight} кг\n"
        f"💰 Стоимость: {price:.2f} ₽"
    )

    # ЕСЛИ ЭТО НЕ ЧИСЛО - ПРОСТО ИГНОР
    if not message.text.isdigit():
        return

    calc_id = int(message.text)

    cursor.execute(
        "SELECT metal, weight, price FROM history WHERE id=?",
        (calc_id,)
    )

    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Расчёт не найден.")
        return

    metal, weight, price = row

    await message.answer(
        f"📂 ДЕТАЛИ РАСЧЁТА\n\n"
        f"🔩 Металл: {metal.capitalize()}\n"
        f"⚖️ Вес: {weight} кг\n"
        f"💰 Стоимость: {price:.2f} ₽"
    )

    if not message.text.isdigit():
        return

    calc_id = int(message.text)

    cursor.execute(
        "SELECT metal, weight, price FROM history WHERE id=?",
        (calc_id,)
    )

    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Расчёт не найден.")
        return

    metal, weight, price = row

    await message.answer(
        f"📂 ДЕТАЛИ РАСЧЁТА\n\n"
        f"🔩 Металл: {metal.capitalize()}\n"
        f"⚖️ Вес: {weight} кг\n"
        f"💰 Стоимость: {price:.2f} ₽"
    )

if __name__ == "__main__":
    asyncio.run(main())