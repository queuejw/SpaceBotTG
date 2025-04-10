# Стандартные параметры корабля
import random


def get_default_ship() -> dict:
    return {
        'default': True,  # Стандартный ли это корабль?
        'active': False,  # Активна ли игра?
        'blocked': False,  # Заблокированы ли действия игроков?
        'on_planet': False,  # Находится ли корабль на планете?
        'air_leaking': False,  # Утечка воздуха
        'fire': False,  # Пожар на корабле
        'planet_name': "Земля",  # Название текущей планеты
        'next_planet_name': "Луна",  # Название следующей планеты
        'previous_planet_name': "Земля",  # Название предыдущей планеты
        'ship_name': "Марс-06",  # Название корабля
        'distance': 0,  # Расстояние от планеты
        'ship_fuel': 100,  # Уровень топлива (от 0 до 100)
        'ship_health': 100,  # Уровень прочности (от 0 до 100)
        'ship_speed': 0,  # Скорость (от 28 000 до 108 000)
        'crew_health': 100,  # Здоровье экипажа (от 0 до 100)
        'crew_oxygen': 100,  # Уровень воздуха (от 0 до 100)
        'resources': 500,  # Количество ресурсов
        'connected_chat': 'null',  # Id чата, с которым в данный момент идёт связь. Если null, значит связи нет.
        'alien_attack': False,  # Атакуют ли пришельцы?
        'extinguishers': random.randint(3, 6),  # Количество огнетушителей на складе
        'bullets': random.randint(3, 6),  # Количество снарядов на складе
        'captain': "null", # Капитан; участник, который первый запустил игру.
        'crew': [], # Id участников, которые имеют доступ к боту
        'engine_damaged': False, # Поврежден ли двигатель?
        'fuel_tank_damaged': False, # Поврежден ли топливный бак?
        'cannon_damaged': False # Повреждено ли орудие?

    }
