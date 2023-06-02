import logging
import asyncpg
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import psycopg2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from psycopg2 import extensions


host = 'host'
port = 'port'
user = 'user'
password = 'password'
database = 'database'

bot = Bot(token='token')
# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot, storage=MemoryStorage())

role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
role_keyboard.add(KeyboardButton('Зарегистрироваться'))
role_keyboard.add(KeyboardButton('Узнать свой id'))
role_keyboard.add(KeyboardButton('Посмотреть лекарства и их id'))
role_keyboard.add(KeyboardButton('Добавить рецепт'))
role_keyboard.add(KeyboardButton('Добавить заказ по рецепту'))
role_keyboard.add(KeyboardButton('Посмотреть информацию о своём заказе'))

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет, я бот производственной аптеки. Что вы хотите сделать:", reply_markup=role_keyboard)

#Зарегистрироваться###############################################################################################

async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i+4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)

@dp.message_handler(lambda message: message.text == "Зарегистрироваться")
async def handle_add_client(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_client(message, chat_id, state)


async def add_client(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите свою фамилию:")
    await AddClientState.PHOTO.set()
    await state.update_data(chat_id=chat_id)


class AddClientState(StatesGroup):
    PHOTO = State()
    NAME = State()
    PATRONYMIC = State()
    BIRTHDATE = State()
    ADDRESS = State()
    PHONE = State()


@dp.message_handler(state=AddClientState.PHOTO)
async def handle_client_surname(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_фамилия = message.text
    await state.update_data(p_фамилия=p_фамилия)
    await bot.send_message(chat_id, "Введите своё имя:")
    await AddClientState.NAME.set()


@dp.message_handler(state=AddClientState.NAME)
async def handle_client_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_имя = message.text
    await state.update_data(p_имя=p_имя)
    await bot.send_message(chat_id, "Введите своё отчество:")
    await AddClientState.PATRONYMIC.set()


@dp.message_handler(state=AddClientState.PATRONYMIC)
async def handle_client_patronymic(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_отчество = message.text
    await state.update_data(p_отчество=p_отчество)
    await bot.send_message(chat_id, "Введите свою дату рождения (ГГГГ-ММ-ДД):")
    await AddClientState.BIRTHDATE.set()


@dp.message_handler(state=AddClientState.BIRTHDATE)
async def handle_client_birthdate(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_дата_рождения = message.text
    await state.update_data(p_дата_рождения=p_дата_рождения)
    await bot.send_message(chat_id, "Введите свой адрес:")
    await AddClientState.ADDRESS.set()


@dp.message_handler(state=AddClientState.ADDRESS)
async def handle_client_address(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_адрес = message.text
    await state.update_data(p_адрес=p_адрес)
    await bot.send_message(chat_id, "Введите свой телефон:")
    await AddClientState.PHONE.set()


@dp.message_handler(state=AddClientState.PHONE)
async def handle_client_phone(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_телефон = message.text
    await state.update_data(p_телефон=p_телефон)

    data = await state.get_data()

    p_фамилия = data.get('p_фамилия')
    p_имя = data.get('p_имя')
    p_отчество = data.get('p_отчество')
    p_дата_рождения = data.get('p_дата_рождения')
    p_адрес = data.get('p_адрес')
    p_телефон = data.get('p_телефон')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        cursor = conn.cursor()

        cursor.execute('CALL ДобавитьКлиента(%s, %s, %s, %s, %s, %s)',
                       (p_фамилия, p_имя, p_отчество, p_дата_рождения, p_адрес, p_телефон))
        conn.commit()

        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Вы успешно зарегистрировались.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при регистрации, попробуйте ещё раз.")

    # Сброс состояния
    await state.finish()

##########Лекарства###################
@dp.message_handler(lambda message: message.text == 'Посмотреть лекарства и их id')
async def handle_production_cost(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM Лекарства')
        rows = cursor.fetchall()

        response = 'Лекарства и их id:\n\n'
        for row in rows:
            medicine_str = f"ID лекарства: {row[0]}\nНазвание: {row[1]}\nСпособ применения: {row[2]}\nСтоимость: {row[3]}\n\n"
            response += medicine_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о лекарствах.")

    cursor.close()
    conn.close()
######################Узнать свой id##########################
@dp.message_handler(lambda message: message.text == "Узнать свой id")
async def handle_get_client_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите фамилию:")
    await GetClientIdState.LAST_NAME.set()
    await state.update_data(chat_id=chat_id)


class GetClientIdState(StatesGroup):
    LAST_NAME = State()
    FIRST_NAME = State()
    PATRONYMIC = State()
    PHONE_NUMBER = State()


@dp.message_handler(state=GetClientIdState.LAST_NAME)
async def handle_get_client_id_last_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    last_name = message.text
    await state.update_data(last_name=last_name)
    await bot.send_message(chat_id, "Введите имя:")
    await GetClientIdState.FIRST_NAME.set()


@dp.message_handler(state=GetClientIdState.FIRST_NAME)
async def handle_get_client_id_first_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    first_name = message.text
    await state.update_data(first_name=first_name)
    await bot.send_message(chat_id, "Введите отчество:")
    await GetClientIdState.PATRONYMIC.set()


@dp.message_handler(state=GetClientIdState.PATRONYMIC)
async def handle_get_client_id_patronymic(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    patronymic = message.text
    await state.update_data(patronymic=patronymic)
    await bot.send_message(chat_id, "Введите телефон:")
    await GetClientIdState.PHONE_NUMBER.set()


@dp.message_handler(state=GetClientIdState.PHONE_NUMBER)
async def handle_get_client_id_phone_number(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    phone_number = message.text

    data = await state.get_data()

    last_name = data.get('last_name')
    first_name = data.get('first_name')
    patronymic = data.get('patronymic')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        cursor = conn.cursor()

        cursor.execute('SELECT "id_клиента" FROM "Клиенты" WHERE "фамилия" = %s AND "имя" = %s AND "отчество" = %s AND "телефон" = %s',
                       (last_name, first_name, patronymic, phone_number))
        result = cursor.fetchone()

        if result:
            client_id = result[0]
            await bot.send_message(chat_id, f"Ваш ID клиента: {client_id}")
        else:
            await bot.send_message(chat_id, "Клиент не найден.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при получении ID клиента.")

    await state.finish()


############Загрузить рецепт#################

@dp.message_handler(lambda message: message.text == "Добавить рецепт")
async def handle_add_recipe(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите ID лекарства:")
    await AddRecipeState.DRUG_ID.set()
    await state.update_data(chat_id=chat_id)


async def add_recipe(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID лекарства:")
    await AddRecipeState.DRUG_ID.set()
    await state.update_data(chat_id=chat_id)


class AddRecipeState(StatesGroup):
    DRUG_ID = State()
    QUANTITY = State()
    CLIENT_ID = State()
    DOCTOR_FULL_NAME = State()


@dp.message_handler(state=AddRecipeState.DRUG_ID)
async def handle_recipe_drug_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    drug_id = message.text
    await state.update_data(drug_id=drug_id)
    await bot.send_message(chat_id, "Введите количество:")
    await AddRecipeState.QUANTITY.set()


@dp.message_handler(state=AddRecipeState.QUANTITY)
async def handle_recipe_quantity(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    quantity = message.text
    await state.update_data(quantity=quantity)
    await bot.send_message(chat_id, "Введите ID клиента:")
    await AddRecipeState.CLIENT_ID.set()


@dp.message_handler(state=AddRecipeState.CLIENT_ID)
async def handle_recipe_client_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    client_id = message.text
    await state.update_data(client_id=client_id)
    await bot.send_message(chat_id, "Введите ФИО врача:")
    await AddRecipeState.DOCTOR_FULL_NAME.set()


@dp.message_handler(state=AddRecipeState.DOCTOR_FULL_NAME)
async def handle_recipe_doctor_full_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    doctor_full_name = message.text
    await state.update_data(doctor_full_name=doctor_full_name)

    data = await state.get_data()

    drug_id = data.get('drug_id')
    quantity = data.get('quantity')
    client_id = data.get('client_id')
    doctor_full_name = data.get('doctor_full_name')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        cursor = conn.cursor()

        cursor.execute('CALL ДобавитьРецепт(%s, %s, %s, %s)',
                       (drug_id, quantity, client_id, doctor_full_name))
        conn.commit()

        cursor.execute('SELECT LASTVAL()')
        recipe_id = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        await bot.send_message(chat_id, f"Рецепт успешно добавлен. ID рецепта: {recipe_id}")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при добавлении рецепта.")

    await state.finish()

#################################добавить заказ#############################

@dp.message_handler(lambda message: message.text == "Добавить заказ по рецепту")
async def handle_add_order(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_order(message, chat_id, state)


async def add_order(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID рецепта:")
    await AddOrderState.RECIPE_ID.set()
    await state.update_data(chat_id=chat_id)


class AddOrderState(StatesGroup):
    RECIPE_ID = State()
    ORDER_DATE = State()


@dp.message_handler(state=AddOrderState.RECIPE_ID)
async def handle_order_recipe_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    recipe_id = message.text
    await state.update_data(recipe_id=recipe_id)
    await bot.send_message(chat_id, "Введите дату заказа (в формате ГГГГ-ММ-ДД):")
    await AddOrderState.ORDER_DATE.set()


@dp.message_handler(state=AddOrderState.ORDER_DATE)
async def handle_order_order_date(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    order_date = message.text

    data = await state.get_data()

    recipe_id = data.get('recipe_id')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        cursor = conn.cursor()

        cursor.execute('CALL Добавить_Заказ(%s, %s)',
                       (recipe_id, order_date))
        conn.commit()

        cursor.execute('SELECT lastval()')
        result = cursor.fetchone()
        order_id = result[0]

        cursor.close()
        conn.close()

        await bot.send_message(chat_id, f"Заказ успешно добавлен. ID заказа: {order_id}")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при добавлении заказа.")

    await state.finish()


###Посмотреть инофрмацию о своём заказе##########################################

@dp.message_handler(lambda message: message.text == "Посмотреть информацию о своём заказе")
async def handle_get_order_info(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите ID заказа:")
    await GetOrderInfoState.ORDER_ID.set()
    await state.update_data(chat_id=chat_id)


class GetOrderInfoState(StatesGroup):
    ORDER_ID = State()
    RECIPE_ID = State()


@dp.message_handler(state=GetOrderInfoState.ORDER_ID)
async def handle_get_order_info_order_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    order_id = message.text
    await state.update_data(order_id=order_id)
    await bot.send_message(chat_id, "Введите ID рецепта:")
    await GetOrderInfoState.RECIPE_ID.set()


@dp.message_handler(state=GetOrderInfoState.RECIPE_ID)
async def handle_get_order_info_recipe_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    recipe_id = message.text

    data = await state.get_data()

    order_id = data.get('order_id')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        cursor = conn.cursor()

        cursor.execute('SELECT * FROM "Заказы" WHERE "id_заказа" = %s AND "id_рецепта" = %s',
                       (order_id, recipe_id))
        result = cursor.fetchone()

        if result:
            order_info = {
                "ID заказа": result[0],
                "ID рецепта": result[1],
                "Дата заказа": result[2],
                "Дата изготовления": result[3],
                "Дата выдачи": result[4],
                "Стоимость": result[5],
            }
            info_message = "Информация о заказе:\n"
            for key, value in order_info.items():
                info_message += f"{key}: {value}\n"
            await bot.send_message(chat_id, info_message)
        else:
            await bot.send_message(chat_id, "Заказ не найден.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при получении информации о заказе.")
    await state.finish()



if __name__ == '__main__':
    logging.info("Бот запущен!")
    executor.start_polling(dp)
