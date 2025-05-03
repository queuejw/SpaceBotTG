def get_normal_role(value: str) -> int:
    match value:
        case "0" | "экипаж" | "обычный" | "э" | "Экипаж" | "Обычный" | "Э":
            print("Член экипажа")
            return 0
        case "1" | "капитан" | "Капитан" | "Кап" | "кап":
            print("Капитан")
            return 1
        case "2" | "инженер" | "инж" | "Инженер" | "Инж":
            print("Инженер")
            return 2
        case "3" | "Стрелок" | "стрелок":
            print("Стрелок")
            return 3
        case _:
            print("Не удалось найти роль, возвращаем -1")
            return -1


def get_role_name_by_num(value: int) -> str:
    match value:
        case 1:
            return "Капитан"
        case 2:
            return "Инженер"
        case 3:
            return "Стрелок"
        case _:
            return "Член экипажа"
