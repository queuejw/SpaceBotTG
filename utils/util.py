# Ограничивает значение в пределах минимального и максимального.
def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def is_it_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False
