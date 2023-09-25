from aiogram.dispatcher.filters.state import StatesGroup, State


class ProfileStatesGroup(StatesGroup):
    language = State()
    offerta = State()
    menu = State()
    tarif = State()
    active = State()
    archive = State()
    paket = State()
    bee_club = State()
    connection = State()
    agree = State()
    uslugi = State()
    postpaid = State()
