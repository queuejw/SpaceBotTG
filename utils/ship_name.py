import random

from utils.check_ship_name import check_name


def create_random_ship_name() -> str:
    random_num = random.randint(1, 255)
    ships = [f"Марс-{random_num}", f"Сатурн-{random_num}", f"Восток-{random_num}", f"Союз-{random_num}",
             f"Восход-{random_num}", f"X-{random_num}", f"Дракон-{random_num}", f"Нептун-{random_num}"]
    name = random.choice(ships)
    if check_name(name):
        return name
    else:
        return create_random_ship_name()
