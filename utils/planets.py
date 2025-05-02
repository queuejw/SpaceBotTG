# Функция для получения списка планет
import os


def get_planets():
    pl_file = "planets.txt"
    if os.path.exists(pl_file):
        with open(pl_file, 'r', encoding='utf-8') as file:
            planets_from_file = [line.strip() for line in file.readlines()]
            file.close()
            return planets_from_file
    # Если не получится, то останавливаем
    print("Планеты не найдены. Остановка.")
    exit(1)
