import logging
import asyncpg
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import psycopg2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from psycopg2 import extensions


# Параметры подключения к базе данных
host = 'host'
port = 'port'
user = 'user'
password = 'password'
database = 'database'

# Создание экземпляра бота
bot = Bot(token='token')
###########################################ПРОСМОТР РОЛЯМИ###################################
# Установка уровня логирования
logging.basicConfig(level=logging.INFO)

# Создание диспетчера
dp = Dispatcher(bot, storage=MemoryStorage())

# Клавиатура с кнопками ролей
role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
role_keyboard.add(KeyboardButton('Продавец'))
role_keyboard.add(KeyboardButton('Директор'))
role_keyboard.add(KeyboardButton('Провизор'))

# Обработчик нажатий кнопок ролей
@dp.message_handler(lambda message: message.text in ["Директор", "Продавец", "Провизор"])
async def handle_role_selection(message: types.Message, state: FSMContext):
    role = message.text
    chat_id = message.chat.id

    if role == 'Директор':
        # Обработка выбранной роли 1
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton("Таблицы для директора"),
            types.KeyboardButton("Процедуры для директора"),
            types.KeyboardButton("Представления для директора"),
            types.KeyboardButton("Назад")
        )
        await message.answer("Выберите действие:", reply_markup=keyboard)
    elif role == 'Продавец':
        # Обработка выбранной роли Продавец
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton("Таблицы для продавца"),
            types.KeyboardButton("Процедуры для продавца"),
            types.KeyboardButton("Представления для продавца"),
            types.KeyboardButton("Назад")
        )
        await message.answer("Выберите действие:", reply_markup=keyboard)
    elif role == 'Провизор':
        # Обработка выбранной роли Провизор
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton("Таблицы для провизора"),
            types.KeyboardButton("Представления для провизора"),
            types.KeyboardButton("Назад")
        )
        await message.answer("Выберите таблицу для просмотра:", reply_markup=keyboard)

    await state.finish()
# Обработчик нажатий кнопки "Таблицы для продавца"
@dp.message_handler(lambda message: message.text == "Таблицы для продавца")
async def handle_tables(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Заказы"),
        types.KeyboardButton("Клиенты"),
        types.KeyboardButton("Изготовляемые лекарства"),
        types.KeyboardButton("Рецепты"),
        types.KeyboardButton("Назад")
    )
    await message.answer("Выберите таблицу для просмотра:", reply_markup=keyboard)
# Обработчик нажатий кнопки "Таблицы для директора"
@dp.message_handler(lambda message: message.text == "Таблицы для директора")
async def handle_tables(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Заказы"),
        types.KeyboardButton("Клиенты"),
        types.KeyboardButton("Изготовляемые лекарства"),
        types.KeyboardButton("Рецепты"),
        types.KeyboardButton("Компоненты"),
        types.KeyboardButton("Склад"),
        types.KeyboardButton("Состав"),
        types.KeyboardButton("Поступление"),
        types.KeyboardButton("Назад")

    )
    await message.answer("Выберите таблицу для просмотра:", reply_markup=keyboard)
# Обработчик нажатий кнопки "Таблицы для провизора"
@dp.message_handler(lambda message: message.text == "Таблицы для провизора")
async def handle_tables(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Состав"),
        types.KeyboardButton("Склад"),
        types.KeyboardButton("Изготовляемые лекарства"),
        types.KeyboardButton("Поступление"),
        types.KeyboardButton("Компоненты"),
        types.KeyboardButton("Рецепты"),
        types.KeyboardButton("Заказы"),
        types.KeyboardButton("Назад")
    )
    await message.answer("Выберите таблицу для просмотра:", reply_markup=keyboard)
# Обработчик нажатий кнопки "Процедуры для продавца"
@dp.message_handler(lambda message: message.text == "Процедуры для продавца")
async def handle_procedures(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Добавить клиента"),
        types.KeyboardButton("Добавить заказ"),
        types.KeyboardButton("Добавить дату выдачи"),
        types.KeyboardButton("Добавить рецепт"),
        types.KeyboardButton("Изменить информацию о клиенте"),
        types.KeyboardButton("Обновить рецепт"),
        types.KeyboardButton("Удалить заказ"),
        types.KeyboardButton("Удалить клиента"),
        types.KeyboardButton("Удалить рецепт"),
        types.KeyboardButton("Назад")
    )
    await message.answer("Выберите процедуру:", reply_markup=keyboard)

# Обработчик нажатий кнопки "Процедуры для директора"
@dp.message_handler(lambda message: message.text == "Процедуры для директора")
async def handle_procedures(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Добавить клиента"),
        types.KeyboardButton("Добавить заказ"),
        types.KeyboardButton("Добавить дату выдачи"),
        types.KeyboardButton("Добавить лекарство"),
        types.KeyboardButton("Добавить рецепт"),
        types.KeyboardButton("Изменить информацию о клиенте"),
        types.KeyboardButton("Обновить лекарство"),
        types.KeyboardButton("Обновить рецепт"),
        types.KeyboardButton("Удалить заказ"),
        types.KeyboardButton("Удалить клиента"),
        types.KeyboardButton("Удалить лекарство"),
        types.KeyboardButton("Удалить рецепт"),
        types.KeyboardButton("Назад")
    )
    await message.answer("Выберите процедуру:", reply_markup=keyboard)
# Обработчик нажатий кнопки "Представление для директора"
@dp.message_handler(lambda message: message.text == "Представления для директора")
async def handle_tables(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('Стоимость производства'),
        types.KeyboardButton('Топ-3 самых заказываемых лекарств'),
        types.KeyboardButton('Наличие компонентов'),
        types.KeyboardButton('Клиенты и количество заказов'),
        types.KeyboardButton('Клиент и телефон'),
        types.KeyboardButton('Информация о рецепте'),
        types.KeyboardButton('Информация о заказах'),
        types.KeyboardButton('Все поступления'),
        types.KeyboardButton("Назад")
    )
    await message.answer("Выберите представлние для просмотра:", reply_markup=keyboard)
# Обработчик нажатий кнопки "Представление для продавца"
@dp.message_handler(lambda message: message.text == "Представления для продавца")
async def handle_tables(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('Топ-3 самых заказываемых лекарств'),
        types.KeyboardButton('Клиенты и количество заказов'),
        types.KeyboardButton('Клиент и телефон'),
        types.KeyboardButton('Информация о рецепте'),
        types.KeyboardButton('Информация о заказах'),
        types.KeyboardButton("Назад")
    )
    await message.answer("Выберите представлние для просмотра:", reply_markup=keyboard)

# Обработчик нажатий кнопки "Представление для произора"
@dp.message_handler(lambda message: message.text == "Представления для провизора")
async def handle_tables(message: types.Message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('Стоимость производства'),
        types.KeyboardButton('Топ-3 самых заказываемых лекарств'),
        types.KeyboardButton('Наличие компонентов'),
        types.KeyboardButton('Информация о рецепте'),
        types.KeyboardButton('Информация о заказах'),
        types.KeyboardButton('Все поступления'),
        types.KeyboardButton("Назад")
    )
    await message.answer("Выберите представлние для просмотра:", reply_markup=keyboard)



async def get_database_connection():
    connection = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    return connection

async def close_database_connection(connection):
    await connection.close()

async def execute_sql_query(query):
    connection = await get_database_connection()
    result = await connection.fetch(query)
    await close_database_connection(connection)
    return result

async def get_orders():
    query = "SELECT * FROM Заказы"
    result = await execute_sql_query(query)
    return result

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет, я бот производственной аптеки. Выберите роль:", reply_markup=role_keyboard)

@dp.message_handler(lambda message: message.text == 'Продавец')
async def seller_role(message: types.Message):
    await message.reply("Вы выбрали роль 'Продавец'.", reply_markup=seller_keyboard)

@dp.message_handler(lambda message: message.text == 'Назад')
async def go_back(message: types.Message):
    await message.reply("Выберите роль:", reply_markup=role_keyboard)

@dp.message_handler(lambda message: message.text == 'Клиенты')
async def view_customers(message: types.Message):
    query = "SELECT * FROM Клиенты"
    result = await execute_sql_query(query)
    response = "Таблица Клиенты:\n\n"
    for row in result:
        response += f"ID клиента: {row['id_клиента']}\n"
        response += f"Фамилия: {row['фамилия']}\n"
        response += f"Имя: {row['имя']}\n"
        response += f"Отчество: {row['отчество']}\n"
        response += f"Дата рождения: {row['дата_рождения']}\n"
        response += f"Адрес: {row['адрес']}\n"
        response += f"Телефон: {row['телефон']}\n"
        response += f"\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=seller_keyboard)

@dp.message_handler(lambda message: message.text == 'Рецепты')
async def view_prescriptions(message: types.Message):
    query = "SELECT * FROM Рецепты"
    result = await execute_sql_query(query)
    response = "Таблица Рецепты:\n\n"
    for row in result:
        response += f"ID рецепта: {row['id_рецепта']}\n"
        response += f"ID лекарства: {row['id_лекарства']}\n"
        response += f"Количество: {row['количество']}\n"
        response += f"ID клиента: {row['id_клиента']}\n"
        response += f"ФИО врача: {row['ФИО_врача']}\n"
        response += f"\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=seller_keyboard)

@dp.message_handler(lambda message: message.text == 'Заказы')
async def view_orders(message: types.Message):
    orders = await get_orders()
    response = "Таблица Заказы:\n\n"
    for row in orders:
        response += f"ID заказа: {row['id_заказа']}\n"
        response += f"ID рецепта: {row['id_рецепта']}\n"
        response += f"Дата заказа: {row['дата_заказа']}\n"
        response += f"Дата изготовления: {row['дата_изготовления']}\n"
        response += f"Дата выдачи: {row['дата_выдачи']}\n"
        response += f"Стоимость заказа: {row['стоимость_заказа']}\n"
        response += f"\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=seller_keyboard)

@dp.message_handler(lambda message: message.text == 'Провизор')
async def pharmacist_role(message: types.Message):
    await message.reply("Вы выбрали роль 'Провизор'.", reply_markup=pharmacist_keyboard)

@dp.message_handler(lambda message: message.text == 'Склад')
async def view_inventory(message: types.Message):
    query = "SELECT * FROM Склад"
    result = await execute_sql_query(query)
    response = "Таблица Склад:\n\n"
    for row in result:
        response += f"ID товара на складе: {row['id_товара_на_складе']}\n"
        response += f"Количество на складе: {row['количество_на_складе']}\n"
        response += f"\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=pharmacist_keyboard)

@dp.message_handler(lambda message: message.text == 'Поступление')
async def view_deliveries(message: types.Message):
    query = "SELECT * FROM Поступление"
    result = await execute_sql_query(query)
    response = "Таблица Поступление:\n\n"
    for row in result:
        response += f"ID поступления: {row['id_поступления']}\n"
        response += f"ID товара на складе: {row['id_товара_на_складе']}\n"
        response += f"Количество: {row['количество']}\n"
        response += f"Дата поступления: {row['дата_поступления']}\n"
        response += f"Дата истечения срока годности: {row['дата_истечения_срока_годности']}\n"
        response += f"\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=pharmacist_keyboard)

@dp.message_handler(lambda message: message.text == 'Изготовляемые лекарства')
async def view_manufactured_medicines(message: types.Message):
    query = "SELECT * FROM \"Изготовляемые лекарства\""
    result = await execute_sql_query(query)
    response = "Таблица 'Изготовляемые лекарства':\n\n"
    for row in result:
        response += f"ID лекарства: {row['id_лекарства']}\n"
        response += f"Название: {row['название']}\n"
        response += f"Способ применения: {row['способ_применения']}\n"
        response += f"Способ приготовления: {row['способ_приготовления']}\n"
        response += f"Стоимость производства: {row['стоимость_производства']}\n"
        response += "\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=pharmacist_keyboard)

@dp.message_handler(lambda message: message.text == 'Компоненты')
async def view_components(message: types.Message):
    query = "SELECT * FROM \"Компоненты\""
    result = await execute_sql_query(query)
    response = "Таблица 'Компоненты':\n\n"
    for row in result:
        response += f"ID компонента: {row['id_компонента']}\n"
        response += f"ID товара на складе: {row['id_товара_на_складе']}\n"
        response += f"Название: {row['название']}\n"
        response += f"Форма: {row['форма']}\n"
        response += f"Стоимость: {row['стоимость']}\n"
        response += f"Критическая норма: {row['критическая_норма']}\n"
        response += "\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=pharmacist_keyboard)

@dp.message_handler(lambda message: message.text == 'Состав')
async def view_composition(message: types.Message):
    query = "SELECT * FROM \"Состав\""
    result = await execute_sql_query(query)
    response = "Таблица 'Состав':\n\n"
    for row in result:
        response += f"ID лекарства: {row['id_лекарства']}\n"
        response += f"ID компонента: {row['id_компонента']}\n"
        response += f"Количество компонента: {row['количество_компонента']}\n"
        response += "\n"
    await send_message_in_parts(message.chat.id, response)
    await message.reply("Выберите действие:", reply_markup=pharmacist_keyboard)

@dp.message_handler(lambda message: message.text == 'Директор')
async def director_role(message: types.Message):
    await message.reply("Вы выбрали роль 'Директор'.", reply_markup=director_keyboard)



async def send_message_in_parts(chat_id, text, max_message_length=4096):
    message_parts = [text[i:i+max_message_length] for i in range(0, len(text), max_message_length)]
    for part in message_parts:
        await bot.send_message(chat_id, part)
##############################################ПРОЦЕДУРЫ###########################################################
###########Добавит Клиента######

# Обработчик нажатия кнопки "Добавить клиента"
@dp.message_handler(lambda message: message.text == "Добавить клиента")
async def handle_add_client(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_client(message, chat_id, state)


# Функция для добавления клиента
async def add_client(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите фамилию клиента:")
    await AddClientState.PHOTO.set()
    await state.update_data(chat_id=chat_id)


# Определение состояний
class AddClientState(StatesGroup):
    PHOTO = State()
    NAME = State()
    PATRONYMIC = State()
    BIRTHDATE = State()
    ADDRESS = State()
    PHONE = State()


# Обработчик состояния фамилии клиента
@dp.message_handler(state=AddClientState.PHOTO)
async def handle_client_surname(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_фамилия = message.text
    await state.update_data(p_фамилия=p_фамилия)
    await bot.send_message(chat_id, "Введите имя клиента:")
    await AddClientState.NAME.set()


# Обработчик состояния имени клиента
@dp.message_handler(state=AddClientState.NAME)
async def handle_client_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_имя = message.text
    await state.update_data(p_имя=p_имя)
    await bot.send_message(chat_id, "Введите отчество клиента:")
    await AddClientState.PATRONYMIC.set()


# Обработчик состояния отчества клиента
@dp.message_handler(state=AddClientState.PATRONYMIC)
async def handle_client_patronymic(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_отчество = message.text
    await state.update_data(p_отчество=p_отчество)
    await bot.send_message(chat_id, "Введите дату рождения клиента:")
    await AddClientState.BIRTHDATE.set()


# Обработчик состояния даты рождения клиента
@dp.message_handler(state=AddClientState.BIRTHDATE)
async def handle_client_birthdate(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_дата_рождения = message.text
    await state.update_data(p_дата_рождения=p_дата_рождения)
    await bot.send_message(chat_id, "Введите адрес клиента:")
    await AddClientState.ADDRESS.set()


# Обработчик состояния адреса клиента
@dp.message_handler(state=AddClientState.ADDRESS)
async def handle_client_address(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_адрес = message.text
    await state.update_data(p_адрес=p_адрес)
    await bot.send_message(chat_id, "Введите телефон клиента:")
    await AddClientState.PHONE.set()


# Обработчик состояния телефона клиента
@dp.message_handler(state=AddClientState.PHONE)
async def handle_client_phone(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_телефон = message.text
    await state.update_data(p_телефон=p_телефон)

    # Получение данных из состояния
    data = await state.get_data()

    # Используйте полученные данные для выполнения операций с базой данных
    p_фамилия = data.get('p_фамилия')
    p_имя = data.get('p_имя')
    p_отчество = data.get('p_отчество')
    p_дата_рождения = data.get('p_дата_рождения')
    p_адрес = data.get('p_адрес')
    p_телефон = data.get('p_телефон')

    try:
        # Установка соединения с базой данных
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        # Создание курсора для выполнения SQL-запросов
        cursor = conn.cursor()

        # Выполнение процедуры "ДобавитьКлиента" с передачей параметров
        cursor.execute('CALL ДобавитьКлиента(%s, %s, %s, %s, %s, %s)',
                       (p_фамилия, p_имя, p_отчество, p_дата_рождения, p_адрес, p_телефон))
        conn.commit()

        # Закрытие курсора и соединения с базой данных
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Клиент успешно добавлен.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при добавлении клиента.")

    # Сброс состояния
    await state.finish()

####################добавить рецепт####################

# Обработчик нажатия кнопки "Добавить рецепт"
@dp.message_handler(lambda message: message.text == "Добавить рецепт")
async def handle_add_recipe(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_recipe(message, chat_id, state)


# Функция для добавления рецепта
async def add_recipe(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID лекарства:")
    await AddRecipeState.DRUG_ID.set()
    await state.update_data(chat_id=chat_id)


# Определение состояний для добавления рецепта
class AddRecipeState(StatesGroup):
    DRUG_ID = State()
    QUANTITY = State()
    CLIENT_ID = State()
    DOCTOR_FULL_NAME = State()


# Обработчик состояния ID лекарства
@dp.message_handler(state=AddRecipeState.DRUG_ID)
async def handle_recipe_drug_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    drug_id = message.text
    await state.update_data(drug_id=drug_id)
    await bot.send_message(chat_id, "Введите количество:")
    await AddRecipeState.QUANTITY.set()


# Обработчик состояния количества
@dp.message_handler(state=AddRecipeState.QUANTITY)
async def handle_recipe_quantity(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    quantity = message.text
    await state.update_data(quantity=quantity)
    await bot.send_message(chat_id, "Введите ID клиента:")
    await AddRecipeState.CLIENT_ID.set()


# Обработчик состояния ID клиента
@dp.message_handler(state=AddRecipeState.CLIENT_ID)
async def handle_recipe_client_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    client_id = message.text
    await state.update_data(client_id=client_id)
    await bot.send_message(chat_id, "Введите ФИО врача:")
    await AddRecipeState.DOCTOR_FULL_NAME.set()


# Обработчик состояния ФИО врача
@dp.message_handler(state=AddRecipeState.DOCTOR_FULL_NAME)
async def handle_recipe_doctor_full_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    doctor_full_name = message.text
    await state.update_data(doctor_full_name=doctor_full_name)

    # Получение данных из состояния
    data = await state.get_data()

    # Используйте полученные данные для выполнения операций с базой данных
    drug_id = data.get('drug_id')
    quantity = data.get('quantity')
    client_id = data.get('client_id')
    doctor_full_name = data.get('doctor_full_name')

    try:
        # Установка соединения с базой данных
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        # Создание курсора для выполнения SQL-запросов
        cursor = conn.cursor()

        # Выполнение процедуры "ДобавитьРецепт" с передачей параметров
        cursor.execute('CALL ДобавитьРецепт(%s, %s, %s, %s)',
                       (drug_id, quantity, client_id, doctor_full_name))
        conn.commit()

        # Закрытие курсора и соединения с базой данных
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Рецепт успешно добавлен.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при добавлении рецепта.")
        # Сброс состояния
    await state.finish()

#################################добавить заказ#############################

# Обработчик нажатия кнопки "Добавить заказ"
@dp.message_handler(lambda message: message.text == "Добавить заказ")
async def handle_add_order(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_order(message, chat_id, state)


# Функция для добавления заказа
async def add_order(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID рецепта:")
    await AddOrderState.RECIPE_ID.set()
    await state.update_data(chat_id=chat_id)


# Определение состояний для добавления заказа
class AddOrderState(StatesGroup):
    RECIPE_ID = State()
    ORDER_DATE = State()


# Обработчик состояния ID рецепта
@dp.message_handler(state=AddOrderState.RECIPE_ID)
async def handle_order_recipe_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    recipe_id = message.text
    await state.update_data(recipe_id=recipe_id)
    await bot.send_message(chat_id, "Введите дату заказа (в формате ГГГГ-ММ-ДД):")
    await AddOrderState.ORDER_DATE.set()


# Обработчик состояния даты заказа
@dp.message_handler(state=AddOrderState.ORDER_DATE)
async def handle_order_order_date(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    order_date = message.text

    # Получение данных из состояния
    data = await state.get_data()

    # Используйте полученные данные для выполнения операций с базой данных
    recipe_id = data.get('recipe_id')

    try:
        # Установка соединения с базой данных
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        # Создание курсора для выполнения SQL-запросов
        cursor = conn.cursor()

        # Выполнение процедуры "ДобавитьЗаказ" с передачей параметров
        cursor.execute('CALL Добавить_Заказ(%s, %s)',
                       (recipe_id, order_date))
        conn.commit()

        # Закрытие курсора и соединения с базой данных
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Заказ успешно добавлен.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при добавлении заказа.")

    # Сброс состояния
    await state.finish()

###################добавить дату выдачи######################

# Обработчик нажатия кнопки "Добавить дату выдачи"
@dp.message_handler(lambda message: message.text == "Добавить дату выдачи")
async def handle_add_delivery_date(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_delivery_date(message, chat_id, state)


# Функция для добавления даты выдачи заказа
async def add_delivery_date(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID заказа:")
    await AddDeliveryDateState.ORDER_ID.set()
    await state.update_data(chat_id=chat_id)


# Определение состояний для добавления даты выдачи
class AddDeliveryDateState(StatesGroup):
    ORDER_ID = State()


# Обработчик состояния ID заказа
@dp.message_handler(state=AddDeliveryDateState.ORDER_ID)
async def handle_delivery_order_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    order_id = message.text

    # Получение данных из состояния
    data = await state.get_data()



    try:
        # Установка соединения с базой данных
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        # Создание курсора для выполнения SQL-запросов
        cursor = conn.cursor()

        # Выполнение процедуры "ДобавитьДатуВыдачи" с передачей параметров
        cursor.execute('CALL ДобавитьДатуВыдачи(%s)', (order_id,))
        conn.commit()

        # Закрытие курсора и соединения с базой данных
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Дата выдачи успешно добавлена.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при добавлении даты выдачи.")

    # Сброс состояния
    await state.finish()

################добавить лекарство##############################################

# Обработчик нажатия кнопки "Добавить лекарство"
@dp.message_handler(lambda message: message.text == "Добавить лекарство")
async def handle_add_medication(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_medication(message, chat_id, state)


# Функция для добавления лекарства
async def add_medication(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите название лекарства:")
    await AddMedicationState.NAME.set()
    await state.update_data(chat_id=chat_id)


# Определение состояний для добавления лекарства
class AddMedicationState(StatesGroup):
    NAME = State()
    APPLICATION_METHOD = State()
    PREPARATION_METHOD = State()
    PRODUCTION_COST = State()
    COMPONENTS = State()
    COMPONENTS_AMOUNT = State()


# Обработчик состояния названия лекарства
@dp.message_handler(state=AddMedicationState.NAME)
async def handle_medication_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    medication_name = message.text

    # Сохранение названия лекарства в состоянии
    await state.update_data(medication_name=medication_name)

    await bot.send_message(chat_id, "Введите способ применения лекарства:")
    await AddMedicationState.APPLICATION_METHOD.set()


# Обработчик состояния способа применения лекарства
@dp.message_handler(state=AddMedicationState.APPLICATION_METHOD)
async def handle_medication_application_method(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    application_method = message.text

    # Сохранение способа применения лекарства в состоянии
    await state.update_data(application_method=application_method)

    await bot.send_message(chat_id, "Введите способ приготовления лекарства:")
    await AddMedicationState.PREPARATION_METHOD.set()


# Обработчик состояния способа приготовления лекарства
@dp.message_handler(state=AddMedicationState.PREPARATION_METHOD)
async def handle_medication_preparation_method(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    preparation_method = message.text

    # Сохранение способа приготовления лекарства в состоянии
    await state.update_data(preparation_method=preparation_method)

    await bot.send_message(chat_id, "Введите стоимость производства лекарства:")
    await AddMedicationState.PRODUCTION_COST.set()


# Обработчик состояния стоимости производства лекарства
@dp.message_handler(state=AddMedicationState.PRODUCTION_COST)
async def handle_medication_production_cost(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    production_cost = message.text

    # Сохранение стоимости производства лекарства в состоянии
    await state.update_data(production_cost=production_cost)

    await bot.send_message(chat_id, "Введите компоненты лекарства в фигурных скобках через запятую:")
    await AddMedicationState.COMPONENTS.set()


# Обработчик состояния компонентов лекарства
@dp.message_handler(state=AddMedicationState.COMPONENTS)
async def handle_medication_components(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    components = message.text

    # Сохранение компонентов лекарства в состоянии
    await state.update_data(components=components)

    await bot.send_message(chat_id, "Введите количество компонентов лекарства в фигурных скобках через запятую:")
    await AddMedicationState.COMPONENTS_AMOUNT.set()


# Обработчик состояния количества компонентов лекарства
@dp.message_handler(state=AddMedicationState.COMPONENTS_AMOUNT)
async def handle_medication_components_amount(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    components_amount = message.text

    # Получение всех данных из состояния
    data = await state.get_data()
    medication_name = data.get('medication_name')
    application_method = data.get('application_method')
    preparation_method = data.get('preparation_method')
    production_cost = data.get('production_cost')
    components = data.get('components')

    try:
        # Установка соединения с базой данных
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        # Создание курсора для выполнения SQL-запросов
        cursor = conn.cursor()

        # Выполнение процедуры "ДобавитьЛекарство" с передачей параметров
        cursor.execute('CALL ДобавитьЛекарство(%s, %s, %s, %s, %s, %s)',
                       (medication_name, application_method, preparation_method, production_cost, components, components_amount))
        conn.commit()

        # Закрытие курсора и соединения с базой данных
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Лекарство успешно добавлено.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при добавлении лекарства.")

    # Сброс состояния
    await state.finish()

########################Удалить заказ########################################

# Обработчик нажатия кнопки "Удалить заказ"
@dp.message_handler(lambda message: message.text == "Удалить заказ")
async def handle_delete_order(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await delete_order(message, chat_id, state)


# Функция для удаления заказа
async def delete_order(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID заказа:")
    await DeleteOrderState.ORDER_ID.set()
    await state.update_data(chat_id=chat_id)


# Определение состояний для удаления заказа
class DeleteOrderState(StatesGroup):
    ORDER_ID = State()


# Обработчик состояния ID заказа для удаления заказа
@dp.message_handler(state=DeleteOrderState.ORDER_ID)
async def handle_delete_order_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    order_id = message.text

    # Получение данных из состояния
    data = await state.get_data()

    # Используйте полученные данные для выполнения операций с базой данных
    # order_id = data.get('order_id')

    try:
        # Установка соединения с базой данных
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

        # Создание курсора для выполнения SQL-запросов
        cursor = conn.cursor()

        # Выполнение процедуры "УдалитьЗаказ" с передачей параметров
        cursor.execute('CALL УдалитьЗаказ(%s)', (order_id,))
        conn.commit()

        # Закрытие курсора и соединения с базой данных
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Заказ успешно удален.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при удалении заказа.")

    # Сброс состояния
    await state.finish()

#################удалить рецепт###############################
@dp.message_handler(lambda message: message.text == "Удалить рецепт")
async def handle_delete_prescription(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await delete_prescription(message, chat_id, state)


async def delete_prescription(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID рецепта:")
    await DeletePrescriptionState.PRESCRIPTION_ID.set()
    await state.update_data(chat_id=chat_id)


class DeletePrescriptionState(StatesGroup):
    PRESCRIPTION_ID = State()


@dp.message_handler(state=DeletePrescriptionState.PRESCRIPTION_ID)
async def handle_delete_prescription_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    prescription_id = message.text

    data = await state.get_data()

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute('CALL УдалитьРецепт(%s)', (prescription_id,))
        conn.commit()
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Рецепт успешно удален.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при удалении рецепта.")

    await state.finish()


#####################удалить клиента#######################
@dp.message_handler(lambda message: message.text == "Удалить клиента")
async def handle_delete_client(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await delete_client(message, chat_id, state)


async def delete_client(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID клиента:")
    await DeleteClientState.CLIENT_ID.set()
    await state.update_data(chat_id=chat_id)


class DeleteClientState(StatesGroup):
    CLIENT_ID = State()


@dp.message_handler(state=DeleteClientState.CLIENT_ID)
async def handle_delete_client_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    client_id = message.text

    data = await state.get_data()

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute('CALL УдалитьКлиента(%s)', (client_id,))
        conn.commit()
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Клиент успешно удален.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при удалении клиента.")

    await state.finish()

#################изменить информацию о клиенте######################################

@dp.message_handler(lambda message: message.text == "Изменить информацию о клиенте")
async def handle_update_client_info(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await update_client_info(message, chat_id, state)


async def update_client_info(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID клиента:")
    await UpdateClientInfoState.CLIENT_ID.set()
    await state.update_data(chat_id=chat_id)


class UpdateClientInfoState(StatesGroup):
    CLIENT_ID = State()
    LAST_NAME = State()
    FIRST_NAME = State()
    MIDDLE_NAME = State()
    BIRTH_DATE = State()
    ADDRESS = State()
    PHONE = State()


@dp.message_handler(state=UpdateClientInfoState.CLIENT_ID)
async def handle_update_client_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    client_id = message.text

    await bot.send_message(chat_id, "Введите фамилию клиента:")
    await UpdateClientInfoState.LAST_NAME.set()
    await state.update_data(client_id=client_id)


@dp.message_handler(state=UpdateClientInfoState.LAST_NAME)
async def handle_update_last_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    last_name = message.text

    await bot.send_message(chat_id, "Введите имя клиента:")
    await UpdateClientInfoState.FIRST_NAME.set()
    await state.update_data(last_name=last_name)


@dp.message_handler(state=UpdateClientInfoState.FIRST_NAME)
async def handle_update_first_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    first_name = message.text

    await bot.send_message(chat_id, "Введите отчество клиента:")
    await UpdateClientInfoState.MIDDLE_NAME.set()
    await state.update_data(first_name=first_name)


@dp.message_handler(state=UpdateClientInfoState.MIDDLE_NAME)
async def handle_update_middle_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    middle_name = message.text

    await bot.send_message(chat_id, "Введите дату рождения клиента:")
    await UpdateClientInfoState.BIRTH_DATE.set()
    await state.update_data(middle_name=middle_name)


@dp.message_handler(state=UpdateClientInfoState.BIRTH_DATE)
async def handle_update_birth_date(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    birth_date = message.text

    await bot.send_message(chat_id, "Введите адрес клиента:")
    await UpdateClientInfoState.ADDRESS.set()
    await state.update_data(birth_date=birth_date)


@dp.message_handler(state=UpdateClientInfoState.ADDRESS)
async def handle_update_address(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    address = message.text

    await bot.send_message(chat_id, "Введите телефон клиента:")
    await UpdateClientInfoState.PHONE.set()
    await state.update_data(address=address)


@dp.message_handler(state=UpdateClientInfoState.PHONE)
async def handle_update_phone(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    phone = message.text

    data = await state.get_data()
    client_id = data.get('client_id')
    last_name = data.get('last_name')
    first_name = data.get('first_name')
    middle_name = data.get('middle_name')
    birth_date = data.get('birth_date')
    address = data.get('address')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute('CALL ИзменитьИнформациюОКлиенте(%s, %s, %s, %s, %s, %s, %s)',
                       (client_id, last_name, first_name, middle_name, birth_date, address, phone))
        conn.commit()
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Информация о клиенте успешно изменена.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при изменении информации о клиенте.")

    await state.finish()

#########################Обновить рецепт#################################

@dp.message_handler(lambda message: message.text == "Обновить рецепт")
async def handle_update_prescription(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await update_prescription(message, chat_id, state)


async def update_prescription(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID рецепта:")
    await UpdatePrescriptionState.PRESCRIPTION_ID.set()
    await state.update_data(chat_id=chat_id)


class UpdatePrescriptionState(StatesGroup):
    PRESCRIPTION_ID = State()
    MEDICATION_ID = State()
    QUANTITY = State()
    CLIENT_ID = State()
    DOCTOR_NAME = State()


@dp.message_handler(state=UpdatePrescriptionState.PRESCRIPTION_ID)
async def handle_update_prescription_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    prescription_id = message.text

    await bot.send_message(chat_id, "Введите ID лекарства:")
    await UpdatePrescriptionState.MEDICATION_ID.set()
    await state.update_data(prescription_id=prescription_id)


@dp.message_handler(state=UpdatePrescriptionState.MEDICATION_ID)
async def handle_update_medication_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    medication_id = message.text

    await bot.send_message(chat_id, "Введите количество лекарства:")
    await UpdatePrescriptionState.QUANTITY.set()
    await state.update_data(medication_id=medication_id)


@dp.message_handler(state=UpdatePrescriptionState.QUANTITY)
async def handle_update_quantity(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    quantity = message.text

    await bot.send_message(chat_id, "Введите ID клиента:")
    await UpdatePrescriptionState.CLIENT_ID.set()
    await state.update_data(quantity=quantity)


@dp.message_handler(state=UpdatePrescriptionState.CLIENT_ID)
async def handle_update_client_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    client_id = message.text

    await bot.send_message(chat_id, "Введите ФИО врача:")
    await UpdatePrescriptionState.DOCTOR_NAME.set()
    await state.update_data(client_id=client_id)


@dp.message_handler(state=UpdatePrescriptionState.DOCTOR_NAME)
async def handle_update_doctor_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    doctor_name = message.text

    data = await state.get_data()
    prescription_id = data.get('prescription_id')
    medication_id = data.get('medication_id')
    quantity = data.get('quantity')
    client_id = data.get('client_id')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute('CALL ОбновитьРецепт(%s, %s, %s, %s, %s)',
                       (prescription_id, medication_id, quantity, client_id, doctor_name))
        conn.commit()
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Рецепт успешно обновлен.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при обновлении рецепта.")

    await state.finish()

################################Обновить лекарство##############

@dp.message_handler(lambda message: message.text == "Обновить лекарство")
async def handle_update_medication(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await update_medication(message, chat_id, state)


async def update_medication(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID лекарства:")
    await UpdateMedicationState.MEDICATION_ID.set()
    await state.update_data(chat_id=chat_id)


class UpdateMedicationState(StatesGroup):
    MEDICATION_ID = State()
    NAME = State()
    USAGE = State()
    PREPARATION = State()
    COST = State()


@dp.message_handler(state=UpdateMedicationState.MEDICATION_ID)
async def handle_update_medication_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    medication_id = message.text

    await bot.send_message(chat_id, "Введите название лекарства:")
    await UpdateMedicationState.NAME.set()
    await state.update_data(medication_id=medication_id)


@dp.message_handler(state=UpdateMedicationState.NAME)
async def handle_update_medication_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    name = message.text

    await bot.send_message(chat_id, "Введите способ применения лекарства:")
    await UpdateMedicationState.USAGE.set()
    await state.update_data(name=name)


@dp.message_handler(state=UpdateMedicationState.USAGE)
async def handle_update_medication_usage(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    usage = message.text

    await bot.send_message(chat_id, "Введите способ приготовления лекарства:")
    await UpdateMedicationState.PREPARATION.set()
    await state.update_data(usage=usage)


@dp.message_handler(state=UpdateMedicationState.PREPARATION)
async def handle_update_medication_preparation(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    preparation = message.text

    await bot.send_message(chat_id, "Введите стоимость производства лекарства:")
    await UpdateMedicationState.COST.set()
    await state.update_data(preparation=preparation)


@dp.message_handler(state=UpdateMedicationState.COST)
async def handle_update_medication_cost(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    cost = message.text

    data = await state.get_data()
    medication_id = data.get('medication_id')
    name = data.get('name')
    usage = data.get('usage')
    preparation = data.get('preparation')

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute('CALL ОбновитьЛекарство(%s, %s, %s, %s, %s)',
                       (medication_id, name, usage, preparation, cost))
        conn.commit()
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Лекарство успешно обновлено.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при обновлении лекарства.")

    await state.finish()

####################удалить лекарство#################

@dp.message_handler(lambda message: message.text == "Удалить лекарство")
async def handle_delete_medication(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await delete_medication(message, chat_id, state)


async def delete_medication(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите ID лекарства:")
    await DeleteMedicationState.MEDICATION_ID.set()
    await state.update_data(chat_id=chat_id)


class DeleteMedicationState(StatesGroup):
    MEDICATION_ID = State()


@dp.message_handler(state=DeleteMedicationState.MEDICATION_ID)
async def handle_delete_medication_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    medication_id = message.text

    try:
        conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute('CALL УдалитьЛекарство(%s)', (medication_id,))
        conn.commit()
        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Лекарство успешно удалено.")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при удалении лекарства.")

    await state.finish()

###################Представления#######################################

# Функция для отправки сообщений с ограничением по длине
async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        # Если длина сообщения меньше или равна 4096, отправляем его целиком
        await bot.send_message(chat_id, message_text)
    else:
        # Если длина сообщения больше 4096, разбиваем его на части
        parts = [message_text[i:i+4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)

###############################Все поступления###################################################
@dp.message_handler(lambda message: message.text == 'Все поступления')
async def handle_all_entries(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Все_поступления"
        cursor.execute('SELECT * FROM Все_поступления')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Поступления:\n\n'
        for row in rows:
            entry_str = f"ID поступления: {row[0]}\nID товара на складе: {row[1]}\nКоличество: {row[2]}\nДата поступления: {row[3]}\nДата истечения срока годности: {row[4]}\n\n"
            response += entry_str

        # Отправляем сообщение с поступлениями, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении поступлений.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()


##########################Информация о заказах#############################################

# Обработчик для кнопки "Информация о заказах"
@dp.message_handler(lambda message: message.text == 'Информация о заказах')
async def handle_order_information(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Информация_о_заказах"
        cursor.execute('SELECT * FROM Информация_о_заказах')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Информация о заказах:\n\n'
        for row in rows:
            order_str = f"ID заказа: {row[0]}\nДата заказа: {row[1]}\nСтоимость заказа: {row[2]}\nФамилия: {row[3]}\nИмя: {row[4]}\nОтчество: {row[5]}\nТелефон: {row[6]}\nНазвание лекарства: {row[7]}\n\n"
            response += order_str

        # Отправляем сообщение с информацией о заказах, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о заказах.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()

############################информация о рецепте############################################################

# Обработчик для кнопки "Информация о рецепте"
@dp.message_handler(lambda message: message.text == 'Информация о рецепте')
async def handle_prescription_information(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Информация_о_рецепте"
        cursor.execute('SELECT * FROM Информация_о_рецепте')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Информация о рецептах:\n\n'
        for row in rows:
            prescription_str = f"ID рецепта: {row[0]}\nФИО врача: {row[1]}\nID компонента: {row[2]}\nКоличество компонента: {row[3]}\n\n"
            response += prescription_str

        # Отправляем сообщение с информацией о рецептах, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о рецептах.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()


###############Клиент и телефон#####################################################

# Обработчик для кнопки "Клиент и телефон"
@dp.message_handler(lambda message: message.text == 'Клиент и телефон')
async def handle_client_phone(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Клиент_и_телефон"
        cursor.execute('SELECT * FROM Клиент_и_телефон')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Информация о клиентах и телефонах:\n\n'
        for row in rows:
            client_str = f"ID клиента: {row[0]}\nФамилия: {row[1]}\nИмя: {row[2]}\nОтчество: {row[3]}\nТелефон: {row[4]}\n\n"
            response += client_str

        # Отправляем сообщение с информацией о клиентах и телефонах, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о клиентах и телефонах.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()

#######################Клиенты и количетсво заказов###################################################

# Обработчик для кнопки "Клиенты и количество заказов"
@dp.message_handler(lambda message: message.text == 'Клиенты и количество заказов')
async def handle_client_order_count(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Клиента_и_количество_заказов"
        cursor.execute('SELECT * FROM Клиенты_количество_заказов')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Информация о клиентах и количестве заказов:\n\n'
        for row in rows:
            client_str = f"ID клиента: {row[0]}\nФамилия: {row[1]}\nИмя: {row[2]}\nОтчество: {row[3]}\nКоличество заказов: {row[4]}\n\n"
            response += client_str

        # Отправляем сообщение с информацией о клиентах и количестве заказов, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о клиентах и количестве заказов.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()

##################Наличие компонентов#####################################

# Обработчик для кнопки "Наличие компонентов"
@dp.message_handler(lambda message: message.text == 'Наличие компонентов')
async def handle_component_availability(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Наличие_компонентов"
        cursor.execute('SELECT * FROM Наличие_компонентов')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Наличие компонентов на складе:\n\n'
        for row in rows:
            component_str = f"ID товара на складе: {row[0]}\nНазвание: {row[1]}\nФорма: {row[2]}\nКоличество на складе: {row[3]}\n\n"
            response += component_str

        # Отправляем сообщение с информацией о наличии компонентов, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о наличии компонентов.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()

#########################Топ-3 самых заказываемых лекарств######################################

# Обработчик для кнопки "Топ-3 самых заказываемых лекарств"
@dp.message_handler(lambda message: message.text == 'Топ-3 самых заказываемых лекарств')
async def handle_top_ordered_medicines(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Самое_заказываемое_лекарство"
        cursor.execute('SELECT * FROM Самое_заказываемое_лекарство')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Топ-3 самых заказываемых лекарств:\n\n'
        for row in rows:
            medicine_str = f"ID лекарства: {row[0]}\nНазвание: {row[1]}\nКоличество: {row[2]}\n\n"
            response += medicine_str

        # Отправляем сообщение с информацией о топ-3 самых заказываемых лекарствах, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о топ-3 самых заказываемых лекарствах.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()

##########################Стоимость производства################################

# Обработчик для кнопки "Стоимость производства"
@dp.message_handler(lambda message: message.text == 'Стоимость производства')
async def handle_production_cost(message: types.Message, state: FSMContext):
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cursor = conn.cursor()

    try:
        # Выполняем SQL-запрос к представлению "Стоимость_производства"
        cursor.execute('SELECT * FROM Стоимость_производства')
        rows = cursor.fetchall()

        # Формируем ответ для пользователя
        response = 'Стоимость производства лекарств:\n\n'
        for row in rows:
            medicine_str = f"ID лекарства: {row[0]}\nНазвание: {row[1]}\nСпособ применения: {row[2]}\nСтоимость производства: {row[3]}\n\n"
            response += medicine_str

        # Отправляем сообщение с информацией о стоимости производства лекарств, учитывая ограничение по длине
        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о стоимости производства лекарств.")

    # Закрываем соединение с базой данных
    cursor.close()
    conn.close()

######################################################################################
# Запуск бота
if __name__ == '__main__':
    logging.info("Бот запущен!")
    executor.start_polling(dp)
