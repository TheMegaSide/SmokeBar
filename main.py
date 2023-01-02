import logging
from typing import Optional
import psycopg2
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
conn = psycopg2.connect(dbname='postgres', user='postgres', password='12345', host='localhost')
cursor = conn.cursor()
TOKEN = "5922515777:AAGII3tdL8L9h7jd-KmObXUb3o3EBS7RFLw"
dp = Dispatcher()


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    product: Optional[int]
    category: Optional[int]


@dp.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, <b>{message.from_user.full_name} !</b>")
    kb = [
        [types.KeyboardButton(text="Поды")],
        # [types.KeyboardButton(text="Одноразки")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True
                                         )
    await message.answer("Выберите категорию товаров", reply_markup=keyboard)


# input_field_placeholder="Выберите способ подачи"
def get_product_keyboard(product_: int, category_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Добавить в корзину",
        callback_data=NumbersCallbackFactory(action="add", product=product_, category=category_))
    return builder.as_markup()


@dp.message(F.text == "Поды")
async def with_puree(message: types.Message):
    cursor.execute('SELECT * FROM products WHERE count > 0')
    records = cursor.fetchall()
    products = {}
    for row in records:
        products[row[0]] = row
    for i in range(len(products)):
        product = str(products.get(i + 1)[1])
        price = str(products.get(i + 1)[2])
        answer = product + "-" + price + "\n"
        await message.answer("Товар: " + answer,
                             reply_markup=get_product_keyboard(products.get(i + 1)[0], products.get(i + 1)[6]))
    kb = [
        [types.KeyboardButton(text="Корзина")],
        [types.KeyboardButton(text="Оформить заказ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True
                                         )
    await message.answer("Выберите дальнейшее действие", reply_markup=keyboard)


@dp.callback_query(NumbersCallbackFactory.filter(F.action == "add"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    cursor.execute('insert into korzina(productid, userid, category) values(' + str(callback_data.product) + ',' + str(
        callback.from_user.id) + ',' + str(callback_data.category) + ')')
    conn.commit()
    await callback.message.answer('Товар добавлен в корзину')


@dp.message(F.text == "Корзина")
async def without_puree(message: types.Message):
    query = 'select * from korzina where userid=' + str(message.from_user.id)
    cursor.execute(query)
    records = cursor.fetchall()
    query1 = 'select * from products'
    cursor.execute(query1)
    records1 = cursor.fetchall()
    pods = {}
    for row in records1:
        pods[row[0]] = row
    answer = 'Ваши товары:\n'
    if (len(records) == 0):
        await message.reply("Корзина пуста")
        kb = [
            [types.KeyboardButton(text="Продолжить")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    else:
        for row in records:
            product = str(pods.get(row[1])[1])
            price = str(pods.get(row[1])[2])
            answer = answer + product + "-" + price + "\n"
        await message.reply(answer)
        kb = [
            [types.KeyboardButton(text="Оформить заказ")],
            [types.KeyboardButton(text="Очистить")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите дальнейшие действия", reply_markup=keyboard)


@dp.message(F.text == "Очистить")
async def with_puree(message: types.Message):
    query = 'delete from korzina where userid=' + str(message.from_user.id)
    cursor.execute(query)
    conn.commit()
    await message.reply("Корзина очищена!")


@dp.message(F.text == "Оформить заказ")
async def with_puree(message: types.Message):
    query = 'select * from korzina where userid=' + str(message.from_user.id)
    cursor.execute(query)
    records = cursor.fetchall()
    korzina = {}
    for row in records:
        korzina[row[0]] = row
    if len(korzina)==0:
        await message.answer("Корзина пуста, добавьте товары в корзину перед заказом")
    else:
        await message.answer("Укажите ваш номер телефона для заказа")


@dp.message()
async def echo_message(message: types.Message):
    if message.text.startswith('+') or message.text.startswith('8'):

        phone = message.text
        query = 'insert into clients(id, phone) values(' + str(
            message.from_user.id) + ',\'' + phone + '\')'
        cursor.execute(query)
        conn.commit()
        await message.answer("Укажите ваш адрес доставки")
    else:
        address = message.text
        query = 'update clients set address=\'' + address + '\' where id=' + str(message.from_user.id)
        cursor.execute(query)
        conn.commit()
        query = 'delete from korzina where userid=' + str(message.from_user.id)
        cursor.execute(query)
        conn.commit()
        await message.answer("Ваш заказ будет доставлен по адресу " + address)


def main() -> None:
    bot = Bot(TOKEN, parse_mode="HTML")

    dp.run_polling(bot)


if __name__ == "__main__":
    main()
