# bot_config.py
import pytz
api_id = 22060480
api_hash = "af947d3f57df924ba38adb773511db17"

KEYWORDS = [
    "обменять рупии", "обменять", "рупии", "рубли", "idr", "обмен",
    "поменяю", "меняет", "рубли рупии", "рупии рубли", "обменник", "курсу",
    "хороший курс", "ищу обмен", "обмен валют", "на карту", "перевод",
    "переводом", "переведу", "наличные", "менялы", "меняла", "доллары", "usd"
]

TRAINER_KEYWORDS = [
    "спортзал", "тренировки", "тренер", "тренировки онлайн", "тренер онлайн",
    "расчет питания", "качалка", "подсушиться", "набрать", "похудеть",
    "тренер оффлайн", "тренер чангу", "тренировки чангу",
    "ищу тренера", "нужен тренер", "ищу тренировки", "хочу тренироваться",
    "персональные тренировки", "фитнес тренер", "посоветуйте тренера"
]



# TARGET_CHAT = "@pavel_healthy"
TARGET_CHAT = "-4865763573"
IGNORED_USERS_FILE = "ignored_users.txt"
STOPWORDS_FILE = "stopwords.txt"
EXTRA_KEYWORDS_FILE = "extra_keywords.txt"
IGNORE_CHATS_FILE = "ignore_chats.txt"
MOSCOW_TZ = pytz.timezone('Europe/Moscow')
START_HOUR = 0    # 00:00 по МСК
END_HOUR = 16     # 16:00 по МСК
name_owner = "САШИ"
welcome_message = (
    "\U0001F6E0️ **Доступные команды:**\n\n"
    "/addword \"слово\" - добавить новое ключевое слово\n"
    "/delword \"слово\" - добавить новое ключевое слово\n"
    "/игнор \"@username\" - добавить пользователя в игнор-лист\n"
    "/неигнор \"@username\" - удалить пользователя из игнор-лист\n"
    "/delchat \"имя чата\" - добавить чат в игнор-лист\n"
    "/lasttime <часы> - вручную просканировать чаты за последние часы\n"
    "/help - показать это сообщение\n\n"
    "/hardscan - 🔥🔥 более полное сканирование(ВКЛЮЧАТЬ ТОЛЬКО ПОСЛЕ ПАДЕНИЯ СИСТЕМЫ)\n\n"
    "‼️ Пиши команды в любом месте (Избранное, группы, ЛС)."
)