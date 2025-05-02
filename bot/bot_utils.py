# Функция для загрузки корабля
import json
import os


# Стандартный конфиг
def get_default_config() -> dict:
    return {
        "token": "",
        "blacklist": "[]",
        "administrators": "[]",
        "config_version": 0
    }


# Функция для загрузки конфига
def load_config() -> dict:
    file = os.path.join("config.json")
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return data
    else:
        save_config(get_default_config())
        print("Создан файл конфигурации.")
        return {}


# Функция для сохранения конфига
def save_config(new_config: dict):
    file = os.path.join("config.json")
    with open(file, "w", encoding="utf-8") as f:
        f.write(json.dumps(new_config, indent=4))
        print("Конфигурация обновлена.")
        f.close()
