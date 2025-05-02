from bot.shared import all_ships, get_crew_str


def get_computer_text(chat_id: int) -> str:
    state = all_ships[chat_id]
    captain = all_ships[chat_id]['crew'][0]['user_name']
    if not state["on_planet"]:
        # В космосе
        text = (
            "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
            "=============\n"
            f"🚀Корабль {state['ship_name']}\n"
            f"👑 Капитан корабля: {captain}\n"
            "=============\n"
            f"📏Расстояние: {state['distance']} км\n"
            f"🪐Следующий объект: {state['next_planet_name']}\n"
            f"🌎Предыдущий объект: {state['previous_planet_name']}\n"
            "=============\n"
            f"🛡️Прочность корабля: {state['ship_health']}%\n"
            f"⛽️Уровень топлива: {state['ship_fuel']}%\n"
            f"🚀Скорость корабля: {state['ship_speed']} км/ч\n"
            "=============\n"
            f"💨Уровень воздуха: {state['oxygen']}%\n"
            f"📦Количество ресурсов: {state['resources']}\n"
        )
        return text
    else:
        # На планете
        text = (
            "📺БОРТОВОЙ КОМПЬЮТЕР📺\n"
            "=============\n"
            f"🚀Корабль {state['ship_name']}\n"
            f"👑 Капитан корабля: {captain}\n"
            "=============\n"
            f"🌎Мы находимся на планете: {state['planet_name']}\n"
            "=============\n"
            f"🛡️Прочность корабля: {state['ship_health']}%\n"
            f"⛽️Уровень топлива: {state['ship_fuel']}%\n"
            "=============\n"
            f"💨Уровень воздуха: {state['oxygen']}%\n"
            f"📦Количество ресурсов: {state['resources']}\n"
        )
    return text


# Выводит информацию об экипаже корабля чата
def get_specific_crew_text(chat_id: int, user_data) -> str:
    is_int = type(user_data) == type(0)
    for i in all_ships[chat_id]['crew']:
        if is_int:
            if i['user_id'] == int(user_data):
                return get_crew_str(i)
        else:
            if i['user_name'] == str(user_data):
                return get_crew_str(i)

    return "⚠️ Компьютер не нашёл этого члена экипажа.\n"


# Функция для получения текста склада
def get_storage_text(chat_id: int) -> str:
    state = all_ships[chat_id]
    return (f"📦 Склад корабля {state['ship_name']} 📦\n"
            "=============\n"
            f"📦 Ресурсы: {state['resources']}\n"
            f"🧯 Огнетушители: {state['extinguishers']}\n"
            f"🔫 Снаряды: {state['bullets']}\n")
