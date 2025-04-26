from aiogram.fsm.state import State, StatesGroup


class Broadcast(StatesGroup):
    message = State()
    confirm = State()
