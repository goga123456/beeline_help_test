import logging
import os

from aiogram import types, executor, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils.executor import start_webhook

from config import TOKEN_API
from markups.inline_mrkps import *
from markups.reply_mrkps import *
from markups.reply_mrkps import markup_language
from messages import *
from states import ProfileStatesGroup

storage = MemoryStorage()
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
#bot = Bot(TOKEN_API)
dp = Dispatcher(bot,
                storage=storage)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(chat_id=message.from_user.id,
                           text="Здравстуйте, Вы соединились с официальныи Ботом Beeline Uzbekistan, для продолжения выберите соотвествующий язык. \n\nAssalomu aleykum, Beeline Uzbekistan Rasmiy boti bilan bog'landingiz, davom etirish uchun kerakli tilni tanlang.",
                           reply_markup=markup_language)
    if state is None:
        return
    await state.finish()


@dp.message_handler(content_types=['text'])
async def lang_choose(message: types.Message, state: FSMContext) -> None:
    try:
        async with state.proxy() as data:
            data['lang'] = message.text
        offerta_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(lang_dict['send_contact'][data['lang']], request_contact=True)
        offerta_menu.row(btn1)
        path_name = "data/CV Георгий Буканов.pdf"
        doc = open(path_name, 'rb')
        await bot.send_document(message.chat.id, doc, caption=lang_dict['offerta'][data['lang']], reply_markup=offerta_menu)

        await ProfileStatesGroup.offerta.set()
    except KeyError:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Выберите вариант кнопкой!")


@dp.message_handler(content_types = types.ContentType.CONTACT, state=ProfileStatesGroup.offerta)
async def number_send(message: types.Message, state: FSMContext) -> None:
    try:
        async with state.proxy() as data:
            if message.text == lang_dict['send_contact'][data['lang']]:
                data['number'] = message.contact.phone_number

            await bot.send_message(chat_id=message.from_user.id,
                                   text=f"Твой номер успешно получен: {message.contact.phone_number}",
                                   reply_markup=types.ReplyKeyboardRemove())
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['start_msg'][data['lang']],
                                   reply_markup=main_menu)
            await ProfileStatesGroup.menu.set()

    except KeyError:
        await bot.send_message(chat_id=message.from_user.id,
                           text="Выберите вариант кнопкой!")










@dp.message_handler(state=ProfileStatesGroup.connection)
async def agree(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['message'] = message.text
    await bot.send_message(chat_id=message.from_user.id, text=lang_dict['do_you_want'][data['lang']],
                           reply_markup=get_agree_kb())
    await ProfileStatesGroup.agree.set()



@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.menu)
async def menu(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['tarif'][data['lang']]:

            tarif_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['active_tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['archive_tarif'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['back'][data['lang']])
            tarif_choose.row(btn1, btn2).row(btn3)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_tarif'][data['lang']],
                                   reply_markup=tarif_choose)
            await ProfileStatesGroup.tarif.set()

        if message.text == lang_dict['paket'][data['lang']]:

            paket_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['month_paket'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['week_paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['day_paket'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['back'][data['lang']])
            paket_choose.row(btn1, btn2, btn3).row(btn4)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_paket'][data['lang']],
                                   reply_markup=paket_choose)
            await ProfileStatesGroup.paket.set()

        if message.text == lang_dict['bee_club'][data['lang']]:

            bee_club_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['first_level'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['second_level'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['third_level'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['forth_level'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['back'][data['lang']])
            bee_club_choose.row(btn1, btn2).row(btn3, btn4).row(btn5)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['beeline_club'][data['lang']],
                                   reply_markup=bee_club_choose)
            await ProfileStatesGroup.bee_club.set()
        if message.text == lang_dict['uslugi'][data['lang']]:
            usluga_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['digital'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['rouming'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['spec'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['base'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['back'][data['lang']])
            usluga_choose.row(btn1, btn2).row(btn3, btn4).row(btn5)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usluga'][data['lang']],
                                   reply_markup=usluga_choose)
            await ProfileStatesGroup.uslugi.set()
        if message.text == lang_dict['news'][data['lang']]:

            news_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['news1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['news2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['news3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['news4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news5'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            news_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_news'][data['lang']],
                                   reply_markup=news_choose)

        if message.text == lang_dict['akciya'][data['lang']]:

            akciya_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['akciya1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['akciya2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['akciya3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['akciya4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['akciya5'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            akciya_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_akciya'][data['lang']],
                                   reply_markup=akciya_choose)

        if message.text == lang_dict['offices'][data['lang']]:
            office_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['office1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['office2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['office3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['office4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['office5'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            office_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_office'][data['lang']],
                                   reply_markup=office_choose)
        if message.text == lang_dict['uridic_doks'][data['lang']]:
            uridik_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['public_offerta'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['rukovodstvo'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['back'][data['lang']])
            uridik_choose.row(btn1, btn2).row(btn3)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_doc'][data['lang']],
                                   reply_markup=uridik_choose)
        if message.text == lang_dict['postpaid'][data['lang']]:
            postpaid_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['back'][data['lang']])
            postpaid_choose.row(btn1, btn2).row(btn3).row(btn4)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_postpaid'][data['lang']],
                                   reply_markup=postpaid_choose)
            await ProfileStatesGroup.postpaid.set()
        if message.text == lang_dict['contacts'][data['lang']]:
            contact_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['number'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['chat'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['telega'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['insta'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['facebook'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            contact_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_connect'][data['lang']],
                                   reply_markup=contact_choose)
        if message.text == lang_dict['connection'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['problem'][data['lang']])
            await ProfileStatesGroup.connection.set()
        if message.text == lang_dict['back'][data['lang']]:
            offerta_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['send_contact'][data['lang']], request_contact=True)
            offerta_menu.row(btn1)
            path_name = "data/CV Георгий Буканов.pdf"
            doc = open(path_name, 'rb')
            await bot.send_document(message.chat.id, doc, caption=lang_dict['offerta'][data['lang']],
                                    reply_markup=offerta_menu)
            await ProfileStatesGroup.offerta.set()


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.tarif)
async def menu_tarif(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['active_tarif'][data['lang']]:
            active_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['yana1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['yana2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['yana3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['yana4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['gold'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['silver'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['back'][data['lang']])
            active_choose.row(btn1, btn2, btn3).row(btn4, btn5, btn6).row(btn7)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['active'][data['lang']],
                                   reply_markup=active_choose)
            await ProfileStatesGroup.active.set()


        if message.text == lang_dict['archive_tarif'][data['lang']]:
            archive_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['zor2'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['yangixit'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['back'][data['lang']])
            archive_choose.row(btn1, btn2).row(btn3)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['archive'][data['lang']],
                                   reply_markup=archive_choose)
            await ProfileStatesGroup.archive.set()

        if message.text == lang_dict['back'][data['lang']]:
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['start_msg'][data['lang']],
                                   reply_markup=main_menu)
            await ProfileStatesGroup.menu.set()

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.active)
async def menu_active(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['yana1'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="yana1 инфа")
        if message.text == lang_dict['yana2'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="yana2 инфа")
        if message.text == lang_dict['yana3'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="yana3 инфа")
        if message.text == lang_dict['yana4'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="yana4 инфа")
        if message.text == lang_dict['gold'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Статус gold инфа")
        if message.text == lang_dict['silver'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Статус silver инфа")
        if message.text == lang_dict['back'][data['lang']]:
            tarif_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['active_tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['archive_tarif'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['back'][data['lang']])
            tarif_choose.row(btn1, btn2).row(btn3)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_tarif'][data['lang']],
                                   reply_markup=tarif_choose)
            await ProfileStatesGroup.tarif.set()


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.archive)
async def menu_archive(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['zor2'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Zor2 инфа")

        if message.text == lang_dict['yangixit'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Yangi Xit инфа")

        if message.text == lang_dict['back'][data['lang']]:
            tarif_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['active_tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['archive_tarif'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['back'][data['lang']])
            tarif_choose.row(btn1, btn2).row(btn3)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_tarif'][data['lang']],
                                   reply_markup=tarif_choose)
            await ProfileStatesGroup.tarif.set()

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.paket)
async def menu_paket(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['month_paket'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Список пакетов")
        if message.text == lang_dict['week_paket'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Список пакетов")
        if message.text == lang_dict['day_paket'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Список пакетов")
        if message.text == lang_dict['back'][data['lang']]:
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)

            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['start_msg'][data['lang']],
                                   reply_markup=main_menu)
            await ProfileStatesGroup.menu.set()

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.bee_club)
async def menu_bee_club(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['first_level'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Привелегия и бонусы")
        if message.text == lang_dict['second_level'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Привелегия и бонусы")
        if message.text == lang_dict['third_level'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Привелегия и бонусы")
        if message.text == lang_dict['forth_level'][data['lang']]:
            await bot.send_message(chat_id=message.from_user.id, text="Привелегия и бонусы")
        if message.text == lang_dict['back'][data['lang']]:
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['start_msg'][data['lang']],
                                   reply_markup=main_menu)
            await ProfileStatesGroup.menu.set()


@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.uslugi)
async def menu_uslugi(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['digital'][data['lang']]:
            uslugi_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['beel_tv'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['beel_music'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['beel_visa'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['yandex_plus'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['beegudok'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            uslugi_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usl'][data['lang']],
                                   reply_markup=uslugi_choose)
        if message.text == lang_dict['rouming'][data['lang']]:
            rouming_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['rouming_pak1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['rouming_pak2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['rouming_pak3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['rouming_pak4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['back'][data['lang']])
            rouming_choose.row(btn1, btn2).row(btn3, btn4).row(btn5)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usl'][data['lang']],
                                   reply_markup=rouming_choose)
        if message.text == lang_dict['spec'][data['lang']]:
            spec_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['spec_1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['spec_2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['spec_3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['spec_4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['back'][data['lang']])
            spec_choose.row(btn1, btn2).row(btn3, btn4).row(btn5)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usl'][data['lang']],
                                   reply_markup=spec_choose)
        if message.text == lang_dict['base'][data['lang']]:
            base_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['base_1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['base_2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['base_3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['base_4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['back'][data['lang']])
            base_choose.row(btn1, btn2).row(btn3, btn4).row(btn5)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usl'][data['lang']],
                                   reply_markup=base_choose)
        if message.text == lang_dict['back'][data['lang']]:
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['start_msg'][data['lang']],
                                   reply_markup=main_menu)
            await ProfileStatesGroup.menu.set()

@dp.message_handler(content_types=['text'], state=ProfileStatesGroup.postpaid)
async def menu_postpaid(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        if message.text == lang_dict['tarif'][data['lang']]:
            pp_tarif_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['pp_tarif1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['pp_tarif2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['pp_tarif3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['pp_tarif4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['pp_tarif5'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            pp_tarif_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usl'][data['lang']],
                                   reply_markup=pp_tarif_choose)

        if message.text == lang_dict['uslugi'][data['lang']]:
            pp_uslugi_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['pp_usluga1'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['pp_usluga2'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['pp_usluga3'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['pp_usluga4'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['pp_usluga5'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            pp_uslugi_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usl'][data['lang']],
                                   reply_markup=pp_uslugi_choose)

        if message.text == lang_dict['paket'][data['lang']]:
            pp_paket_choose = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['beel_tv'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['beel_music'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['beel_visa'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['yandex_plus'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['beegudok'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['back'][data['lang']])
            pp_paket_choose.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['choose_usl'][data['lang']],
                                   reply_markup=pp_paket_choose)
        if message.text == lang_dict['back'][data['lang']]:
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)
            await bot.send_message(chat_id=message.from_user.id, text=lang_dict['start_msg'][data['lang']],
                                   reply_markup=main_menu)
            await ProfileStatesGroup.menu.set()

@dp.callback_query_handler(state=ProfileStatesGroup.agree)
async def calendar_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'next':
        async with state.proxy() as data:
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)
            await bot.send_message(chat_id=callback_query.from_user.id, text=f"/{data['message']}")
            await bot.send_message(chat_id=callback_query.from_user.id, text="Вскоре наш оператор вам ответит", reply_markup=main_menu)
            await callback_query.message.delete()
            await ProfileStatesGroup.menu.set()

    if callback_query.data == 'close':
        async with state.proxy() as data:
            main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            btn1 = types.KeyboardButton(lang_dict['tarif'][data['lang']])
            btn2 = types.KeyboardButton(lang_dict['paket'][data['lang']])
            btn3 = types.KeyboardButton(lang_dict['bee_club'][data['lang']])
            btn4 = types.KeyboardButton(lang_dict['uslugi'][data['lang']])
            btn5 = types.KeyboardButton(lang_dict['news'][data['lang']])
            btn6 = types.KeyboardButton(lang_dict['akciya'][data['lang']])
            btn7 = types.KeyboardButton(lang_dict['offices'][data['lang']])
            btn8 = types.KeyboardButton(lang_dict['uridic_doks'][data['lang']])
            btn9 = types.KeyboardButton(lang_dict['postpaid'][data['lang']])
            btn10 = types.KeyboardButton(lang_dict['contacts'][data['lang']])
            btn11 = types.KeyboardButton(lang_dict['connection'][data['lang']])
            btn12 = types.KeyboardButton(lang_dict['back'][data['lang']])
            main_menu.row(btn1, btn2, btn3).row(btn4, btn5).row(btn6, btn7, btn8).row(btn9, btn10).row(btn11).row(btn12)
            await bot.send_message(chat_id=callback_query.from_user.id, text=lang_dict['start_msg'][data['lang']],
                                   reply_markup=main_menu)
            await callback_query.message.delete()
            await ProfileStatesGroup.menu.set()

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()

if __name__ == '__main__':
    #executor.start_polling(dp,
                           #skip_updates=True)
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
