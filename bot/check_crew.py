# Проверяем здоровье у всех участников. Если на нуле - удаляем. Если погибает капитан, передаем роль случайному участнику

import random

from bot.messages import send_message
from bot.shared import all_ships
from utils.roles import get_role_name_by_num


# Получаем случайного игрока
def get_random_crew(data: list, captain: dict) -> dict:
    user: dict = random.choice(data)
    if user == captain:
        # Совпадение, пробуем ещё раз
        return get_random_crew(data, captain)
    return user


# Проверка здоровья
async def check_all_crew(chat_id: int):
    for player in all_ships[chat_id]['crew']:
        if player['user_health'] < 1:
            print("игрок умер")
            if player['user_role'] == 1:
                if len(all_ships[chat_id]['crew']) > 1:
                    print("это был капитан, передаем роль")
                    new_captain = get_random_crew(all_ships[chat_id]['crew'], player)
                    all_ships[chat_id]['crew'].remove(new_captain)
                    new_captain['user_role'] = 1
                    all_ships[chat_id]['crew'][0] = new_captain
                    await send_message(chat_id,
                                       f"Капитан {player['user_name']} погиб! 😵\nВстречайте нового капитана: {all_ships[chat_id]['crew'][0]['user_name']} 👑")
                else:
                    print("это был капитан, но роль передать не получится. просто удаляю")
                    all_ships[chat_id]['crew'].remove(player)
                    await send_message(chat_id,
                                       f"Капитан {player['user_name']} погиб! 😵")
            else:
                print("это был игрок, просто удаляем")
                all_ships[chat_id]['crew'].remove(player)
                await send_message(chat_id,
                                   f"{get_role_name_by_num(int(player['user_role']))} {player['user_name']} погиб 😵")
