import datetime
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
bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher()


def main() -> None:
    dp.run_polling(bot)


class BasketCallbackFactory(CallbackData, prefix="bask"):
    action: str
    product: Optional[int]
    category: Optional[int]


class OrderCallbackFactory(CallbackData, prefix="order"):
    action: str
    client: int
    order_id: int


@dp.message(Command(commands=["start"]))
async def main_menu(message: Message) -> None:
    await message.answer(f"Hello, <b>{message.from_user.full_name} !</b>")
    kb = [
        [types.KeyboardButton(text="Поды")],
        [types.KeyboardButton(text="Одноразки")],
        [types.KeyboardButton(text="Жидкости")],
        [types.KeyboardButton(text="Расходники")],
        [types.KeyboardButton(text="Корзина")],
        [types.KeyboardButton(text="Мои заказы")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите категорию товаров", reply_markup=keyboard)


def add_product_builder(product_: int, category_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Добавить в корзину",
        callback_data=BasketCallbackFactory(action="add", product=product_, category=category_))
    return builder.as_markup()


def take_order(client_: int, order_id_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Принять заказ",
        callback_data=OrderCallbackFactory(action="take", client=client_, order_id=order_id_)
    )
    return builder.as_markup()


def end_order(client_: int, order_id_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Заказ отдан",
        callback_data=OrderCallbackFactory(action="end", client=client_, order_id=order_id_)
    )
    return builder.as_markup()


def send_order(client_: int, order_id_: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Заказ в пути', callback_data=OrderCallbackFactory(action="send", client=client_, order_id=order_id_)
    )
    return builder.as_markup()


@dp.callback_query(OrderCallbackFactory.filter(F.action == "send"))
async def send_order_call(callback: types.CallbackQuery, callback_data: OrderCallbackFactory):
    await bot.send_message(callback_data.client, "Ваш заказ в пути")
    cursor.execute('update sold set state=\'В пути\' where id=' + str(callback_data.order_id))
    conn.commit()
    await bot.send_message(group_id, 'Заказ №' + str(callback_data.order_id) + ' в пути')
    await callback.message.answer("Вы отправились в путь. Нажмите кнопку, когда заказ будет передан клиенту", reply_markup=end_order(callback_data.client, callback_data.order_id))


@dp.callback_query(OrderCallbackFactory.filter(F.action == "end"))
async def send_order_call(callback: types.CallbackQuery, callback_data: OrderCallbackFactory):
    await bot.send_message(callback_data.client, "ВЫ получили ваш заказ. Если что-то пошло не так, свяжитесь с администратором магазина: @ ")
    cursor.execute('update sold set state=\'Выполнен\' where id=' + str(callback_data.order_id))
    conn.commit()
    await bot.send_message(group_id, 'Заказ №' + str(callback_data.order_id) + ' доставлен')
    await callback.message.answer('Вы выполнили заказ №' + str(callback_data.order_id))


@dp.message(F.text == "Поды")
async def pod_selection(message: types.Message):
    cursor.execute('SELECT * FROM products WHERE count > 0 and category = 1')
    records = cursor.fetchall()
    products = {}
    for i in range(len(records)):
        products[records[i][0]] = records[i]

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


@dp.callback_query(OrderCallbackFactory.filter(F.action == "take"))
async def take_order_call(
        callback: types.CallbackQuery,
        callback_data: OrderCallbackFactory
):
    await bot.send_message(callback_data.client, "Ваш заказ в обработке")
    cursor.execute('update sold set state=\'В обработке\' where id=' + str(callback_data.order_id))
    conn.commit()
    await bot.send_message(callback.from_user.id, "Вы приняли заказ. Нажмите кнопку, когда будете готовы",
                           reply_markup=send_order(callback_data.client, callback_data.order_id))
    await callback.message.answer('Заказ №' + str(callback_data.order_id) + ' принят в обработку сотрудником @' + str(
        callback.from_user.username))


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
            [types.KeyboardButton(text="Очистить")],
            [types.KeyboardButton(text="Продолжить заказ")]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите дальнейшие действия", reply_markup=keyboard)


@dp.message(F.text == "Продолжить заказ")
async def main_menu(message: Message) -> None:
    # await message.answer(f"Hello, <b>{message.from_user.full_name} !</b>")
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


@dp.message(F.text == "Мои заказы")
async def orders_list(message: Message) -> None:
    cursor.execute('select * from sold where client=' + str(message.from_user.id))
    records = cursor.fetchall()
    orders = {}
    for row in records:
        orders[row[0]] = row
    answer = ''
    for i in orders.keys():
        answer = answer + 'Ваш заказ от ' + str(orders.get(i)[3])[:-7] + ' - Статус: ' + str(orders.get(i)[4]) + '\n'
    await message.answer(answer)


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
        cursor.execute('Select * from clients where id = ' + str(message.from_user.id))
        records = cursor.fetchall()
        client = {}
        for row in records:
            client[row[0]] = row
        if len(client) == 0:
            await message.answer("Укажите ваш номер телефона для заказа в формате +7 или 8")
        else:
            kb = [
                [types.KeyboardButton(text="Да")],
                [types.KeyboardButton(text="Нет")]
            ]
            keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
            await message.answer("Предыдущий заказ:\nТелефон:" + client.get(message.from_user.id)[1] + '\nАдрес:' +
                                 client.get(message.from_user.id)[2])
            await message.answer("Ваши данные за прошлый заказ еще актуальны?", reply_markup=keyboard)


@dp.message(F.text == "Да")
async def repeated_order(message: types.Message):
    cursor.execute('Select * from clients where id = ' + str(message.from_user.id))
    records = cursor.fetchall()
    client = {}
    for row in records:
        client[row[0]] = row
    await process_order(message.from_user.id, message.from_user.username)


@dp.message(F.text == "Нет")
async def repeated_order(message: types.Message):
    await message.answer("Укажите ваш номер телефона для заказа в формате +7 или 8")


async def process_order(user_id: int, username: str):
    query = 'select * from korzina where userid=' + str(user_id)
    cursor.execute(query)
    records = cursor.fetchall()
    korzina = {}
    for row in records:
        korzina[row[0]] = row
    query = 'select * from clients where id=' + str(user_id)
    cursor.execute(query)
    records = cursor.fetchall()
    clients = {}
    for row in records:
        clients[row[0]] = row
    total = 0
    cursor.execute('SELECT * FROM products')
    records = cursor.fetchall()
    products = {}
    for row in records:
        products[row[0]] = row
    answer = ''
    order = ''
    for i in korzina.keys():
        total = total + products.get(korzina.get(i)[1])[2]
        cursor.execute('update products set count=count-1 where id=' + str(korzina.get(i)[1]))
        conn.commit()
        order += str(korzina.get(i)[1]) + ','
        answer = answer + str(products.get(korzina.get(i)[1])[1]) + ' - ' + str(
            products.get(korzina.get(i)[1])[2]) + '\n'
    order = order[:-1]
    query = 'insert into sold(client, products, date, state) values(' + str(
        user_id) + ', ARRAY[' + order + '],\'' \
            + str(datetime.datetime.now()) + '\', \'Зарегистрирован\')'
    cursor.execute(query)
    conn.commit()
    query = 'select id from sold where client=' + str(user_id) + ' and products = ARRAY[' + order + ']'
    cursor.execute(query)
    records = cursor.fetchall()
    order = {}
    for row in records:
        order[row[0]] = row
    await bot.send_message(group_id,
                           "Пришел заказ №" + str(
                               next(iter(order.items()))[1][0]) + " Покупатель:@" + username
                           + "\nСписок товаров: " + answer +
                           'Сумма=' + str(total) + '\nАдрес:' + next(iter(clients.items()))[1][2] + '\nТелефон:' + next(iter(clients.items()))[1][1],
                           reply_markup=take_order(user_id, next(iter(order.items()))[1][0]))

    query = 'delete from korzina where userid=' + str(user_id)
    cursor.execute(query)
    conn.commit()


@dp.message()
async def catch_phone_address(message: types.Message):
    if message.text.startswith('+') or message.text.startswith('8'):

        phone = message.text
        query = 'insert into clients(id, phone, username) values(' + str(
            message.from_user.id) + ',\'' + phone + '\', \'@'+message.from_user.username+'\')'
        cursor.execute(query)
        conn.commit()
        await message.answer("Укажите ваш адрес доставки")
    else:
        address = message.text
        query = 'update clients set address=\'' + address + '\' where id=' + str(message.from_user.id)
        cursor.execute(query)
        conn.commit()

        await message.answer("Ваш заказ будет доставлен по адресу " + address)
        await process_order(message.from_user.id, message.from_user.username)


if __name__ == "__main__":
    main()
