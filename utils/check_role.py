from bot.shared import get_user_by_id


def check_role(role: int, chat_id: int, user_id: int):
    user_role = int(get_user_by_id(chat_id, user_id)['user_role'])
    if user_role != role and role != 1:
        return False
    else:
        return True
