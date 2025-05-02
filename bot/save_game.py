# Костыль для перепроверки данных

from bot import chat_utils
from bot.shared import all_ships
from utils.util import clamp


def check_data(state: dict, chat_id: int):
    state["ship_fuel"] = clamp(state["ship_fuel"], 0, 100)
    state["ship_health"] = clamp(state["ship_health"], 0, 100)
    state["oxygen"] = clamp(state["oxygen"], 0, 100)
    state["extinguishers"] = clamp(state["extinguishers"], 0, 256)
    state["bullets"] = clamp(state["bullets"], 0, 128)
    all_ships[chat_id] = state
    return state


# Функция для сохранения данных
def check_and_save_data(state: dict, chat_id: int):
    chat_utils.save_chat_state(chat_id, check_data(state, chat_id))
