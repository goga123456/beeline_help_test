import asyncio
import logging
import time
import os
import re
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.utils.executor import start_webhook
from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import schedule
from openpyxl import load_workbook
import states
from markups.keyboard import *
from markups.markup_kalendar import get_birthday_kb, get_birthday_month_kb, get_birthday_day_kb, get_birthday_year_kb
from markups.reply_markups_start_and_back import get_start_kb, get_start_and_back_kb
from messages import *
from states import ProfileStatesGroup, AdminStatesGroup
from aiogram.utils.exceptions import ChatNotFound
import aiohttp
from db import Database
from aiogram.utils.exceptions import MessageCantBeDeleted

storage = MemoryStorage()
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

dp = Dispatcher(bot,
                storage=storage)

async def create_and_send_excel():
    file_name = await baza.create_excel()
    with open(file_name, 'rb') as document:
        await bot.send_document(chat_id="-1002017595145", document=document)

scheduler = AsyncIOScheduler()
baza = Database()

@dp.message_handler(commands=['admin'])
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id == 6478221968 or message.from_user.id == 94766813 or message.from_user.id == 5452154717:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Введите chat_id")
        await states.AdminStatesGroup.chat_id.set()



@dp.message_handler(content_types=['text'], state=states.AdminStatesGroup.chat_id)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    if message.text == '/start':
        await state.finish()
        await bot.send_message(chat_id=message.from_user.id,
                               text=start_msg,
                               reply_markup=get_initial_kb())
    else:
        async with state.proxy() as data:
            data['chat_id'] = message.text
        await bot.send_message(chat_id=message.from_user.id,
                               text="Введите сообщение")
        await states.AdminStatesGroup.message.set()



@dp.message_handler(content_types=['text'], state=states.AdminStatesGroup.message)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    try:
        if message.text == '/start':
            await state.finish()
            await bot.send_message(chat_id=message.from_user.id,
                                   text=start_msg,
                                   reply_markup=get_initial_kb())
        else:
            async with state.proxy() as data:
                data['message'] = message.text
            await bot.send_message(chat_id=data['chat_id'],
                                   text=data['message'])
            await state.finish()
    except ChatNotFound:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Неверный chat_id, введите заново")
        await states.AdminStatesGroup.chat_id.set()


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text=start_msg,
                           reply_markup=get_initial_kb())
    if state is None:
        return
    await state.finish()


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.cause_of_rejection)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    if len(message.text) > 254:  # Corrected the parenthesis position
        await bot.send_message(chat_id=message.from_user.id,
                               text="Текст слишком длинный, введите заново")
        await ProfileStatesGroup.cause_of_rejection.set()
    else:
        async with state.proxy() as data:
            data['cause'] = message.text
            now = datetime.now()
            response_date = now.strftime("%d.%m.%Y %H:%M:%S")
            chat_id = message.from_user.id
            await bot.send_message(chat_id="-1002017595145",
                                   text=f"Дата отклика: {response_date}\n\n"
                                        f"Причина отказа {data['cause']}\n"
                                        f"Chat_id: {chat_id}")
            await baza.reject(now, data['cause'])
        await bot.send_message(chat_id=message.from_user.id,
                               text=again)
        await state.finish()
    


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.input_number)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['number'] = message.text
        if str(data['number']).isdigit() and str(data['number']).startswith('998') and len(str(data['number'])) == 12:
            await bot.send_message(chat_id=message.from_user.id,
                                       text=name, reply_markup=get_start_and_back_kb())
            await ProfileStatesGroup.input_name.set()
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                text=wrong_number)  
            
        


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.input_name)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    if not re.match(r'^[а-яА-ЯёЁ\s]+$', message.text):
        await bot.send_message(chat_id=message.from_user.id,
                               text="Используйте только кириллицу")
        return
    async with state.proxy() as data:
        data['name'] = message.text
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.from_user.id,
                               text=number,
                               reply_markup=get_start_kb())
        await ProfileStatesGroup.input_number.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=surname, reply_markup=get_start_and_back_kb())
        await ProfileStatesGroup.input_surname.set()






@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.input_surname)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    if not re.match(r'^[а-яА-ЯёЁ\s]+$', message.text):
        await bot.send_message(chat_id=message.from_user.id,
                               text="Используйте только кириллицу")
        return
    async with state.proxy() as data:
        data['surname'] = message.text
        data['day'] = '-'
        data['month'] = '-'
        data['year'] = '-'
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.from_user.id,
                               text=name)
        await ProfileStatesGroup.input_name.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=date_of_birthday,
                               reply_markup=get_birthday_kb())
        await ProfileStatesGroup.input_birthday.set()


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.input_other_town_and_district)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['town_and_district'] = message.text
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.from_user.id,
                               text=where_are_you_from,
                               reply_markup=get_town_kb())
        await ProfileStatesGroup.input_Tashkent_or_other_town.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=education,
                               reply_markup=get_edu_kb())
        await ProfileStatesGroup.input_edu.set()

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.experience_describe)
async def load_it_info(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['exp'] = message.text
    if message.text == 'Назад':
        await bot.send_message(chat_id=message.from_user.id,
                               text=experience_msg,
                               reply_markup=get_exp_kb())
        await ProfileStatesGroup.input_experience.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=thank_you)
        await bot.send_message(chat_id=message.from_user.id,
                               text=sendmail)
        await bot.send_message(chat_id=message.from_user.id,
                               text=again,
                               reply_markup=get_start_kb())
        now = datetime.now()
        response_date = now.strftime("%d.%m.%Y %H:%M:%S")
        without_spaces = str(data['month']).replace(" ", "")
        birthday = f"{data['day']}.{without_spaces}.{data['year']}"
        chat_id = message.from_user.id

        await bot.send_message(chat_id="-1002017595145",
                               text=f"Дата отклика: {response_date}\n\n"
                                    f"Номер телефона: {data['number']}\n"
                                    f"Имя: {data['name']}\n"
                                    f"Фамилия: {data['surname']}\n"
                                    f"Дата рождения: {birthday}\n"
                                    f"Адрес проживания: {data['town_and_district']}\n"
                                    f"Образование: {data['edu']}\n"
                                    f"Уровень русского: {data['rus']}\n"
                                    f"Уровень узбекского: {data['uzb']}\n"
                                    f"Уровень английского: {data['eng']}\n"
                                    f"Опыт работы: {data['exp']}\n"
                                    f"Chat_id: {chat_id}")
        await baza.zayavka(now, data['surname'], data['name'], data['number'], birthday, data['town_and_district'], data['edu'], data['rus'], data['uzb'], data['eng'], data['exp'])
        await state.finish()

@dp.callback_query_handler()
async def initial_keyboards(callback_query: types.CallbackQuery):
    if callback_query.data == 'next':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=start_msg2,
                               reply_markup=get_initial_kb2())


    if callback_query.data == 'close':
        await ProfileStatesGroup.cause_of_rejection.set()
        await bot.send_message(callback_query.from_user.id, text=cause_of_rejection)
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")


    if callback_query.data == 'yes_i_want':
        await ProfileStatesGroup.input_number.set()
        await bot.send_message(callback_query.from_user.id, text=number, reply_markup=get_start_kb())
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")


    if callback_query.data == 'i_dont_want':
        await ProfileStatesGroup.cause_of_rejection.set()
        await bot.send_message(callback_query.from_user.id, text=cause_of_rejection)
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")


# колбеки на первые 2 сообщения


@dp.callback_query_handler(state=ProfileStatesGroup.input_birthday)
async def calendar_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'day':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=choose_day, reply_markup=get_birthday_day_kb())
        await ProfileStatesGroup.input_day.set()
    if callback_query.data == 'month':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=choose_month, reply_markup=get_birthday_month_kb())
        await ProfileStatesGroup.input_month.set()
    if callback_query.data == 'year':
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=choose_year, reply_markup=get_birthday_year_kb())
        await ProfileStatesGroup.input_year.set()
    if callback_query.data == 'send_birth':
        async with state.proxy() as data:
            if data['day'] == '-' and data['month'] == '-' and data['year'] == '-':
                await bot.send_message(callback_query.message.chat.id, "Дата не выбрана")
            elif data['day'] == '-' and data['month'] == '-':
                await bot.send_message(callback_query.message.chat.id, "День и месяц не выбраны")
            elif data['day'] == '-' and data['year'] == '-':
                await bot.send_message(callback_query.message.chat.id, "День и год не выбраны")
            elif data['month'] == '-' and data['year'] == '-':
                await bot.send_message(callback_query.message.chat.id, "Месяц и год не выбраны")
            elif data['month'] == '-' and data['year'] == '-':
                await bot.send_message(callback_query.message.chat.id, "Месяц и год не выбраны")
            elif data['day'] == '-':
                await bot.send_message(callback_query.message.chat.id, "День не выбран")
            elif data['month'] == '-':
                await bot.send_message(callback_query.message.chat.id, "Месяц не выбран")
            elif data['year'] == '-':
                await bot.send_message(callback_query.message.chat.id, text="Год не выбран")
            elif data['month'] == '0 2' and data['day'] == '30':
                await bot.send_message(callback_query.message.chat.id, text=data_not_exist)
            elif data['month'] == '0 2' and data['day'] == '31':
                await bot.send_message(callback_query.message.chat.id, text=data_not_exist)
            elif data['month'] == '0 4' and data['day'] == '31':
                await bot.send_message(callback_query.message.chat.id, text=data_not_exist)
            elif data['month'] == '0 6' and data['day'] == '31':
                await bot.send_message(callback_query.message.chat.id, text=data_not_exist)
            elif data['month'] == '0 9' and data['day'] == '31':
                await bot.send_message(callback_query.message.chat.id, text=data_not_exist)
            elif data['month'] == '1 1' and data['day'] == '31':
                await bot.send_message(callback_query.message.chat.id, text=data_not_exist)
            else:
                without_spaces = str(data['month']).replace(" ", "")
                now = datetime.now()
                response_date = now.strftime("%d.%m.%Y %H:%M:%S")
                birthday = f"{data['day']}.{without_spaces}.{data['year']}"
                chat_id = callback_query.from_user.id
                if now.year - int(data['year']) < 18:
                    await bot.send_message(callback_query.message.chat.id, text=less_than_18)
                    await bot.send_message(callback_query.message.chat.id, text=again)



                    await bot.send_message(chat_id="-1002017595145",
                                           text=f"Дата отклика: {response_date}\n\n"
                                                f"Номер телефона: {data['number']}\n"
                                                f"Имя: {data['name']}\n"
                                                f"Фамилия: {data['surname']}\n"
                                                f"Дата рождения: {birthday}\n"
                                                f"Chat_id: {chat_id}")
                    await baza.less18(now, data['surname'], data['name'], data['number'], birthday)
                    ###Добавление в базу данных

                    try:
                        await callback_query.message.delete()
                    except MessageCantBeDeleted:
                        print("Перезарустите пожалуйста бот")
                    await state.finish()
                else:
                    try:
                        await callback_query.message.delete()
                    except MessageCantBeDeleted:
                        print("Перезарустите пожалуйста бот")
                    await bot.send_message(chat_id=callback_query.message.chat.id,
                                           text=date_of_birthday)
                    await bot.send_message(callback_query.from_user.id,
                                           text=f"{data['day']}.{without_spaces}.{data['year']}")
                    await bot.send_message(chat_id=callback_query.message.chat.id,
                                           text=where_are_you_from,
                                           reply_markup=get_town_kb())
                    await states.ProfileStatesGroup.input_Tashkent_or_other_town.set()

    if callback_query.data == 'back_to_surname':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=surname,
                               reply_markup=get_start_and_back_kb())
        await ProfileStatesGroup.input_surname.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_day)
async def day_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == '1' or '2' or '3' or '4' or '5' or '6' or '7' or '8' or '9' or '10' or '11' or
            '12' or '13' or '14' or '15' or '16' or '17' or '18' or '19' or '20' or '21' or
            '22' or '23' or '24' or '25' or '26' or '27' or '28' or '29' or '30' or '31'):
        async with state.proxy() as data:
            data['day'] = callback_query.data
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Дата твоего рождения', reply_markup=get_birthday_kb())
        await ProfileStatesGroup.input_birthday.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_month)
async def month_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == '0 1' or '0 2' or '0 3' or '0 4' or '0 5' or '0 6' or '0 7' or '0 8' or
            '0 9' or '1 0' or '1 1' or '1 2'):
        async with state.proxy() as data:
            data['month'] = callback_query.data

        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Дата твоего рождения', reply_markup=get_birthday_kb())
        await ProfileStatesGroup.input_birthday.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_year)
async def year_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (callback_query.data == '1970' or '1972' or '1973' or '1974' or '1975' or '1976' or '1977' or '1978' or
            '1979' or '1980' or '1981' or '1982' or '1983' or '1984' or '1985' or '1986' or '1987' or '1988' or
            '1989' or '1990' or '1991'):
        async with state.proxy() as data:
            data['year'] = callback_query.data
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Дата твоего рождения', reply_markup=get_birthday_kb())
        await ProfileStatesGroup.input_birthday.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_Tashkent_or_other_town)
async def town_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Ташкент':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=where_are_you_from)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=callback_query.data)

        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=district,
                               reply_markup=get_district_kb())
        await ProfileStatesGroup.input_district.set()

    if callback_query.data == 'Другой':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")

        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=drugoi)
        await ProfileStatesGroup.input_other_town_and_district.set()

    if callback_query.data == 'back_to_birth':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=date_of_birthday,
                               reply_markup=get_birthday_kb())
        await ProfileStatesGroup.input_birthday.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_district)
async def district_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (
            callback_query.data == 'Алмазар' or callback_query.data == 'Бектемир' or callback_query.data == 'Мирабад' or callback_query.data == 'Мирзо-Улугбек' or callback_query.data == 'Сергели' or
            callback_query.data == 'Чиланзар' or callback_query.data == 'Шайхантаур' or callback_query.data == 'Юнусабад' or callback_query.data == 'Яккасарай' or callback_query.data == 'Яшнабад' or callback_query.data == 'Учтепа'):
        async with state.proxy() as data:
            data['town_and_district'] = f"Ташкент/{callback_query.data}"
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=district)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=callback_query.data)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=education,
                               reply_markup=get_edu_kb())
        await ProfileStatesGroup.input_edu.set()

    if callback_query.data == 'back_to_town':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=where_are_you_from,
                               reply_markup=get_town_kb())
        await ProfileStatesGroup.input_Tashkent_or_other_town.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_edu)
async def edu_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (
            callback_query.data == 'Высшее' or callback_query.data == 'Неполное высшее' or callback_query.data == 'Среднее' or
            callback_query.data == 'Неполное среднее' or callback_query.data == 'Среднее специальное'):
        async with state.proxy() as data:
            data['edu'] = callback_query.data
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=education)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=callback_query.data)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=rus_lang,
                               reply_markup=get_rus_kb())
        await ProfileStatesGroup.input_rus.set()
    if callback_query.data == 'to_town':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=where_are_you_from,
                               reply_markup=get_town_kb())
        await ProfileStatesGroup.input_Tashkent_or_other_town.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_rus)
async def rus_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (
            callback_query.data == 'Отлично' or callback_query.data == 'Хорошо' or callback_query.data == 'Удовлетворительно' or
            callback_query.data == 'Не владею русским языком'):
        async with state.proxy() as data:
            data['rus'] = callback_query.data
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=rus_lang)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=callback_query.data)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=uzb_lang,
                               reply_markup=get_uzb_kb())
        await ProfileStatesGroup.input_uzb.set()
    if callback_query.data == 'back_to_edu':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=education,
                               reply_markup=get_edu_kb())
        await ProfileStatesGroup.input_edu.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_uzb)
async def uzb_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (
            callback_query.data == 'Отлично знаю' or callback_query.data == 'Хорошо знаю' or callback_query.data == 'Удовлетворительно знаю' or
            callback_query.data == 'Не владею узбекским языком'):
        async with state.proxy() as data:
            data['uzb'] = callback_query.data
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=uzb_lang)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=callback_query.data)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=eng_lang,
                               reply_markup=get_eng_kb())
        await ProfileStatesGroup.input_eng.set()
    if callback_query.data == 'back_to_ru':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=rus_lang,
                               reply_markup=get_rus_kb())
        await ProfileStatesGroup.input_rus.set()


@dp.callback_query_handler(state=ProfileStatesGroup.input_eng)
async def uzb_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if (
            callback_query.data == 'Отлично владею' or callback_query.data == 'Хорошо владею' or callback_query.data == 'Удовлетворительно владею' or
            callback_query.data == 'Не владею английским языком'):
        async with state.proxy() as data:
            data['eng'] = callback_query.data
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=eng_lang)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=callback_query.data)
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=experience_msg,
                               reply_markup=get_exp_kb())
        await ProfileStatesGroup.input_experience.set()
    if callback_query.data == 'back_to_uz':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=uzb_lang,
                               reply_markup=get_uzb_kb())
        await ProfileStatesGroup.input_uzb.set()

@dp.callback_query_handler(state=ProfileStatesGroup.input_experience)
async def exp_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'Есть':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=experience_about)
        await ProfileStatesGroup.experience_describe.set()
    if callback_query.data == 'Нет':
        async with state.proxy() as data:
            data['exp'] = callback_query.data
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")  
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=thank_you)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=sendmail)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=again,
                               reply_markup=get_start_kb())
        now = datetime.now()
        response_date = now.strftime("%d.%m.%Y %H:%M:%S")
        without_spaces = str(data['month']).replace(" ", "")
        birthday = f"{data['day']}.{without_spaces}.{data['year']}"
        chat_id = callback_query.from_user.id

        await bot.send_message(chat_id="-1002017595145",
                               text=f"Дата отклика: {response_date}\n\n"
                                    f"Номер телефона: {data['number']}\n"
                                    f"Имя: {data['name']}\n"
                                    f"Фамилия: {data['surname']}\n"
                                    f"Дата рождения: {birthday}\n"
                                    f"Адрес проживания: {data['town_and_district']}\n"
                                    f"Образование: {data['edu']}\n"
                                    f"Уровень русского: {data['rus']}\n"
                                    f"Уровень узбекского: {data['uzb']}\n"
                                    f"Уровень английского: {data['eng']}\n"
                                    f"Опыт работы: {data['exp']}\n"
                                    f"Chat_id: {chat_id}")
        await baza.zayavka(now, data['surname'], data['name'], data['number'], birthday, data['town_and_district'], data['edu'], data['rus'], data['uzb'], data['eng'], data['exp'])
        await state.finish()
    if callback_query.data == 'back_to_eng':
        try:
            await callback_query.message.delete()
        except MessageCantBeDeleted:
            print("Перезарустите пожалуйста бот")
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=eng_lang,
                               reply_markup=get_eng_kb())
        await ProfileStatesGroup.input_eng.set()




async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True, max_connections=100)
    scheduler.add_job(create_and_send_excel, 'cron', hour=11)
    scheduler.start()



async def on_shutdown(dispatcher):
    await bot.delete_webhook()
    scheduler.shutdown()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )



