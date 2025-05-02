from bot.bot_utils import load_config
from bot.chat_utils import get_planets

CONFIG = load_config()

BLOCKED_CHATS: list = CONFIG['blacklist']
ADMINS: list = CONFIG['administrators']
TOKEN = CONFIG['token']
PLANETS = get_planets()
