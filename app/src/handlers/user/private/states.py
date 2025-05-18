from aiogram.fsm.state import StatesGroup, State


class Info(StatesGroup):
    account_id = State()
    match_id = State()
    nickname = State()
    players_data = State()
    accounts_data = State()
    number_pages_for_match = State()
    number_pages_for_accounts = State()
    page_item = State()


class AnotherInfo(StatesGroup):
    account_id = State()
