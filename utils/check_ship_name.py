# Проверка доступности названия корабля
from bot.shared import all_ships


def check_name(new_name: str) -> bool:
    ships = list(all_ships.items())
    for ship in ships:
        if ship[1]['ship_name'] == new_name:
            return False
    return True
