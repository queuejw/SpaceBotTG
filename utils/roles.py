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
        case "4" | "Пилот" | "пилот":
            print("Пилот")
            return 4
        case "5" | "Связист" | "связист":
            print("Связист")
            return 4
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
        case 4:
            return "Пилот"
        case 5:
            return "Связист"
        case _:
            return "Член экипажа"
