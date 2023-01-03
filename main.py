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
group_id = -828412008
TOKEN = "5922515777:AAGII3tdL8L9h7jd-KmObXUb3o3EBS7RFLw"
bot = Bot(TOKEN)
dp = Dispatcher()


class BasketCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    product: Optional[int]
    category: Optional[int]


class OrderCallbackFactory(CallbackData, prefix="order"):
    client: int


@dp.message(Command(commands=["start"]))
async def main_menu(message: Message) -> None:
    await message.answer(f"Hello, <b>{message.from_user.full_name} !</b>")
    kb = [
        [types.KeyboardButton(text="Поды")],
        [types.KeyboardButton(text="Одноразки")],
        [types.KeyboardButton(text="Жидкости")],
        [types.KeyboardButton(text="Расходники")],
        [types.KeyboardButton(text="Корзина")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True
                                         )
    await message.answer("Выберите категорию товаров", reply_markup=keyboard)


# input_field_placeholder="Выберите способ подачи"
def add_product_builder(product_: int, category_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Добавить в корзину",
        callback_data=BasketCallbackFactory(action="add", product=product_, category=category_))
    return builder.as_markup()


def work_with_order(client_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Принять заказ', callback_data=OrderCallbackFactory(action="take", client=client_)
    )
    return builder.as_markup()


def send_order(client_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Заказ в пути', callback_data=OrderCallbackFactory(action="send", client=client_)
    )
    return builder.as_markup()


@dp.callback_query(OrderCallbackFactory.filter(F.action == "take"))
async def take_order_call(
        callback: types.CallbackQuery,
        callback_data: OrderCallbackFactory
):
    await bot.send_message(callback_data.client, "Ваш заказ в обработке")
    await callback.message.answer('Заказ принят в обработку', reply_markup=send_order(callback_data.client))


@dp.callback_query(OrderCallbackFactory.filter(F.action == "send"))
async def send_order_call(
        callback: types.CallbackQuery,
        callback_data: OrderCallbackFactory
):
    await bot.send_message(callback_data.client, "Ваш заказ в пути")
    await callback.message.answer('Заказ в доставке', reply_markup=send_order(callback_data.client))


@dp.message(F.text == "Поды")
async def pod_selection(message: types.Message):
    cursor.execute('SELECT * FROM products WHERE count > 0 and category = 1')
    records = cursor.fetchall()
    products = {}
    for i in range(len(records)):
        products[records[i][0]] = records[i]
        print(products)
    for i in products.keys():
        product = str(products.get(i)[1])
        price = str(products.get(i)[2])
        answer = product + " - " + price + " р.\n"
        await message.answer("Товар: " + answer,
                             reply_markup=add_product_builder(products.get(i)[0], products.get(i)[6]))
    kb = [
        [types.KeyboardButton(text="Корзина")],
        [types.KeyboardButton(text="Оформить заказ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите дальнейшее действие", reply_markup=keyboard)


@dp.message(F.text == "Одноразки")
async def onetime_selection(message: types.Message):
    cursor.execute('SELECT * FROM products WHERE count > 0 and category = 2')
    records = cursor.fetchall()
    products = {}
    for i in range(len(records)):
        products[records[i][0]] = records[i]
        print(products)
    for i in products.keys():
        product = str(products.get(i)[1])
        price = str(products.get(i)[2])
        answer = product + " - " + price + " р.\n"
        await message.answer("Товар: " + answer,
                             reply_markup=add_product_builder(products.get(i)[0], products.get(i)[6]))
    kb = [
        [types.KeyboardButton(text="Корзина")],
        [types.KeyboardButton(text="Оформить заказ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите дальнейшее действие", reply_markup=keyboard)


@dp.message(F.text == "Жидкости")
async def liquid_selection(message: types.Message):
    cursor.execute('SELECT * FROM products WHERE count > 0 and category = 3')
    records = cursor.fetchall()
    products = {}
    for i in range(len(records)):
        products[records[i][0]] = records[i]
        print(products)
    for i in products.keys():
        product = str(products.get(i)[1])
        price = str(products.get(i)[2])
        answer = product + " - " + price + " р.\n"
        await message.answer("Товар: " + answer,
                             reply_markup=add_product_builder(products.get(i)[0], products.get(i)[6]))
    kb = [
        [types.KeyboardButton(text="Корзина")],
        [types.KeyboardButton(text="Оформить заказ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите дальнейшее действие", reply_markup=keyboard)


@dp.message(F.text == "Расходники")
async def cons_selection(message: types.Message):
    cursor.execute('SELECT * FROM products WHERE count > 0 and category = 4')
    records = cursor.fetchall()
    products = {}
    for i in range(len(records)):
        products[records[i][0]] = records[i]
        print(products)
    for i in products.keys():
        product = str(products.get(i)[1])
        price = str(products.get(i)[2])
        answer = product + " - " + price + " р.\n"
        await message.answer("Товар: " + answer,
                             reply_markup=add_product_builder(products.get(i)[0], products.get(i)[6]))
    kb = [
        [types.KeyboardButton(text="Корзина")],
        [types.KeyboardButton(text="Оформить заказ")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите дальнейшее действие", reply_markup=keyboard)


@dp.callback_query(BasketCallbackFactory.filter(F.action == "add"))
async def add_product_call(
        callback: types.CallbackQuery,
        callback_data: BasketCallbackFactory
):
    cursor.execute('insert into korzina(productid, userid, category) values(' + str(callback_data.product) + ',' + str(
        callback.from_user.id) + ',' + str(callback_data.category) + ')')
    conn.commit()
    await callback.message.answer('Товар добавлен в корзину')


@dp.message(F.text == "Корзина")
async def basket_check(message: types.Message):
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
    if len(records) == 0:
        kb = [
            [types.KeyboardButton(text="Поды")],
            [types.KeyboardButton(text="Одноразки")],
            [types.KeyboardButton(text="Жидкости")],
            [types.KeyboardButton(text="Расходники")],
            [types.KeyboardButton(text="Корзина")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Корзина пуста, добавьте товары в корзину перед заказом", reply_markup=keyboard)

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
async def clean_basket(message: types.Message):
    query = 'delete from korzina where userid=' + str(message.from_user.id)
    cursor.execute(query)
    conn.commit()
    await message.reply("Корзина очищена!")


@dp.message(F.text == "Оформить заказ")
async def order_all(message: types.Message):
    query = 'select * from korzina where userid=' + str(message.from_user.id)
    cursor.execute(query)
    records = cursor.fetchall()
    korzina = {}
    for row in records:
        korzina[row[0]] = row
    if len(korzina) == 0:
        kb = [
            [types.KeyboardButton(text="Поды")],
            [types.KeyboardButton(text="Одноразки")],
            [types.KeyboardButton(text="Жидкости")],
            [types.KeyboardButton(text="Расходники")],
            [types.KeyboardButton(text="Корзина")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Корзина пуста, добавьте товары в корзину перед заказом", reply_markup=keyboard)

    else:
        await message.answer("Укажите ваш номер телефона для заказа в формате +7 или 8")


@dp.message()
async def catch_phone_address(message: types.Message):
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

        await message.answer("Ваш заказ будет доставлен по адресу " + address)
        query = 'select * from korzina where userid=' + str(message.from_user.id)
        cursor.execute(query)
        records = cursor.fetchall()
        korzina = {}
        for row in records:
            korzina[row[1]] = row
        total = 0
        cursor.execute('SELECT * FROM products')
        records = cursor.fetchall()
        products = {}
        for row in records:
            products[row[0]] = row
        answer = ''
        for i in korzina.keys():
            total = total + products.get(i)[2]
            print(products.get(i)[2])
            answer = answer + str(products.get(i)[1]) + ' - ' + str(products.get(i)[2]) + '\n'
        await bot.send_message(group_id, "Пришел заказ: " + answer + 'Сумма=' + str(total),
                               reply_markup=work_with_order(message.from_user.id))
        query = 'delete from korzina where userid=' + str(message.from_user.id)
        cursor.execute(query)
        conn.commit()


def main() -> None:
    bot = Bot(TOKEN, parse_mode="HTML")

    dp.run_polling(bot)


if __name__ == "__main__":
    main()
