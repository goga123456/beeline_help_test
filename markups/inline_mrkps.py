from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_agree_kb() -> InlineKeyboardMarkup:
    kb1 = InlineKeyboardMarkup(resize_keyboard=True)
    b1 = InlineKeyboardButton('Продолжить', callback_data='next')
    b2 = InlineKeyboardButton('Отказаться', callback_data='close')
    kb1.add(b1, b2)
    return kb1