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
        'meteorite_fall': False,  # Падает ли метеорит на планету?
        'alien_attack': False,  # Атакуют ли пришельцы?
        'engine_damaged': False,  # Поврежден ли двигатель?
        'fuel_tank_damaged': False,  # Поврежден ли топливный бак?
        'cannon_damaged': False,  # Повреждено ли орудие?
        'cannon_overheated': False,  # Перегрето ли орудие?
        'planet_name': "Земля",  # Название текущей планеты
        'next_planet_name': "Луна",  # Название следующей планеты
        'previous_planet_name': "Земля",  # Название предыдущей планеты
        'ship_name': "Марс-06",  # Название корабля
        'connected_chat': 'null',  # Id чата, с которым в данный момент идёт связь. Если null, значит связи нет.
        'distance': 0,  # Расстояние от планеты
        'ship_fuel': 100,  # Уровень топлива (от 0 до 100)
        'ship_health': 100,  # Уровень прочности (от 0 до 100)
        'ship_speed': 0,  # Скорость (от 28 000 до 108 000)
        'oxygen': 100,  # Уровень воздуха (от 0 до 100)
        'resources': random.randint(400, 600),  # Количество ресурсов
        'extinguishers': random.randint(3, 6),  # Количество огнетушителей на складе
        'bullets': random.randint(3, 6),  # Количество снарядов на складе
        'crew': []  # Участники, которые имеют собственную роль и доступ к боту
    }
