# alerts.py
import logging
import re
from cashes import alert_cache


logger = logging.getLogger(__name__)

from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_config import TARGET_CHAT



async def send_alert(app, message, keyword_matched, old_message_note="", link=None, force_send=False):
    # Универсальный ключ
    unique_key = f"{message.chat.id}:{message.id}"
    if not force_send and unique_key in alert_cache:
        logging.info("но такое сообщение уже было обработано и отправлено - пропускаем")
        return


    chat_title = message.chat.title if message.chat.title else "Личка / неизвестный чат"
    chat_link = get_chat_link(message)
    if chat_link:
        chat_title_md = escape_markdown(chat_title)
        chat_info = f"📌 Чат: [{chat_title_md}]({chat_link})"
    else:
        chat_info = f"📌 Чат: **{escape_markdown(chat_title)}**"

    # Автор
    if message.from_user:
        if message.from_user.username:
            author = f"👤 Автор: @{message.from_user.username}"
        elif message.from_user.first_name:
            name = escape_markdown(message.from_user.first_name)
            author = f"👤 Автор: [{name}](tg://user?id={message.from_user.id})"
        else:
            author = f"👤 Автор: [Пользователь](tg://user?id={message.from_user.id})"
    else:
        author = "👤 Автор неизвестен"

    # Ссылка на сообщение (Markdown!)
    sms_link = f"\n👉 [Перейти к сообщению]({link})" if link else ""

    alert_message = (
        f"{old_message_note}🔔 Найдено ключевое слово: **{escape_markdown(keyword_matched)}**\n\n"
        f"{chat_info}\n"
        f"{author}\n"
        f"📨 Текст: {escape_markdown(message.text)}"
        f"{sms_link}"
    )

    buttons = []
    if message.from_user and message.from_user.username:
        buttons.append([InlineKeyboardButton(f"🚫 Игнорировать @{message.from_user.username}", callback_data=f"ignore_{message.from_user.username}")])
    if link:
        buttons.append([InlineKeyboardButton("👉 Перейти к сообщению", url=link)])

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    await app.send_message(
        TARGET_CHAT,
        alert_message,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )
    alert_cache.add(unique_key)


from pyrogram.enums import ChatType


def get_message_link(message):
    chat = message.chat
    msg_id = getattr(message, "message_id", None) or getattr(message, "id", None)
    logging.info(
        f"get_message_link: chat_type={chat.type}, message_id={msg_id}, chat_username={getattr(chat, 'username', None)}, chat_id={chat.id}")

    if not msg_id:
        return None

    # Используем enum, а не строки
    if chat.type in {ChatType.SUPERGROUP, ChatType.CHANNEL}:
        if chat.username:
            return f"https://t.me/{chat.username}/{msg_id}"
        elif str(chat.id).startswith("-100"):
            return f"https://t.me/c/{str(chat.id)[4:]}/{msg_id}"

    return None


def get_chat_link(message):
    chat = message.chat
    if chat.type in ["supergroup", "group", "channel"]:
        if chat.username:
            return f"https://t.me/{chat.username}"
        elif str(chat.id).startswith("-100"):
            # Ссылка на приватный канал/супергруппу
            return f"https://t.me/c/{str(chat.id)[4:]}/"
    return None


async def send_startup_message(app):
    await app.send_message(TARGET_CHAT, "🚀 Бот запущен!\n\nНапиши `/help` чтобы узнать команды.")


def escape_markdown(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'([_*\[\]()~`>#+=|{}.!-])', r'\\\1', text)


