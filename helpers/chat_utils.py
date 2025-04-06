import json
import os

from helpers.ship import get_default_ship

# Директория для хранения кораблей
DATA_DIR = "ships"
# создать если нет
os.makedirs(DATA_DIR, exist_ok=True)


# Функция для получения токена бота из файла token.txt
def get_token() -> str:
    token_file = "token.txt"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            result = f.read()
            f.close()
            return result
    # Если не получится, то останавливаем
    print("Токен не найден. Остановка.")
    exit(1)


# Функция для получения списка планет
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


def get_chat_folder(chat_id: int) -> str:
    print(f"Получаю папку для чата {chat_id}")
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
        with open(state_file, "r") as f:
            return json.load(f)

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
        f.write(json.dumps(state))
