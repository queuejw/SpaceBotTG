# Здесь функции для сохранения

import json
import os

from utils.ship import get_default_ship

# Директория для хранения кораблей
DATA_DIR = "ships"
# создать если нет
os.makedirs(DATA_DIR, exist_ok=True)


def get_chat_folder(chat_id: int) -> str:
    return os.path.join(DATA_DIR, str(chat_id))


# Функция для получения пути к файлу корабля
def get_chat_state_file(chat_id: int) -> str:
    print(f"Получаю файл корабля чата {chat_id}")
    return os.path.join(get_chat_folder(chat_id), "ship.json")


# Функция для удаления корабля
def delete_chat_state(chat_id: int):
    print(f"Пытаюсь удалить корабль чата {chat_id}")
    state_file = get_chat_state_file(chat_id)
    if os.path.exists(state_file):
        os.remove(state_file)
        print(f"Корабль чата {chat_id} удален")


# Функция для загрузки корабля
def load_chat_state(chat_id: int) -> dict:
    state_file = get_chat_state_file(chat_id)

    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            ship = json.load(f)
            f.close()
            return ship

    # Если файл не существует, инициализируем новое состояние
    print(f"Не получилось получить корабль, возвращаем стандартный.")
    return get_default_ship()


# Функция для сохранения корабля
def save_chat_state(chat_id: int, state: dict):
    print(f"Сохраняю данные корабля чата {chat_id}")
    chat_folder = get_chat_folder(chat_id)
    os.makedirs(chat_folder, exist_ok=True)

    state_file = get_chat_state_file(chat_id)
    with open(state_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(state, indent=4, ensure_ascii=False))
        f.close()
