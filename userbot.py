import asyncio
from pyrogram import Client, filters, idle

import datetime
import pytz  # pip install pytz

import logging
import datetime


from bot_config import api_id, api_hash, TARGET_CHAT, name_owner, START_HOUR, END_HOUR, MOSCOW_TZ
from keyword_manager import get_all_keywords
from ignore_manager import load_ignored_users, load_ignored_chats, load_stopwords
from cashes import alert_cache_cleaner
from alerts import send_alert, get_message_link, send_startup_message
from service_maethods import contains_stopphrase





from commands import CommandHandler


ALL_KEYWORDS = get_all_keywords()
ignored_users = load_ignored_users()
ignored_chats = load_ignored_chats()

app = Client("my_account", api_id=api_id, api_hash=api_hash)
command_handler = CommandHandler(app, ALL_KEYWORDS, ignored_users, ignored_chats)

logging.basicConfig(
    level=logging.WARNING,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)



@app.on_message(filters.text)
async def keyword_alert(client, message):
    logging.info(f"Получено сообщение: {message}")
    try:
        chat_username = getattr(message.chat, "username", None)
        chat_id = str(message.chat.id)
        if chat_id in command_handler.ignored_chats or (chat_username and chat_username.lower() in command_handler.ignored_chats):
            return
        sender = message.from_user.username if message.from_user else None
        is_self = getattr(message.from_user, "is_self", False)
        text = message.text.lower() or ""

        # 1. Если сообщение в TARGET_CHAT
        if (
                (chat_username and chat_username.lower() == TARGET_CHAT.lstrip("@").lower())
                or (TARGET_CHAT.startswith("-100") and chat_id == TARGET_CHAT) or  (str(message.chat.id) == TARGET_CHAT)
        ):


            # 1.1 Если это команда (начинается с /), обрабатываем
            if text.startswith("/"):
                # Обработка команд
                if text.startswith("/help"):
                    await command_handler.send_help(message)
                    return
                if text.startswith("/addword"):
                    await command_handler.add_word(message)
                    return
                if text.startswith("/delword"):  # новая команда для удаления ключевого слова
                    await command_handler.del_word(message)
                    return
                if text.startswith("/игнор"):
                    await command_handler.ignore_user(message)
                    return
                if text.startswith("/неигнор"):  # новая команда для удаления пользователя из игнора
                    await command_handler.unignore_user(message)
                    return
                if text.startswith("/delchat"):
                    await command_handler.del_chat(message)
                    return
                if text.startswith("/lasttime"):
                    await command_handler.last_time(message)
                    return
                if text.startswith("/hardscan"):
                    await scheduler_loop()
                    return
                # --- Команды стоп-слов ---
                if text.startswith("/stopword"):
                    await command_handler.add_stopword(message)
                    return
                if text.startswith("/unstopword"):
                    await command_handler.remove_stopword(message)
                    return
                await message.reply(f"\U0001F50E неверная команда - еще раз так напишешь  я тебе устрою!")
                return
            return
            # раскоментить когда будет в один чат писаться
            # else:
            #     await message.reply(f"\U0001F50E ты че написал не правильно баклан?! а?")
            #     return

        # 2. Если сообщение не из TARGET_CHAT

        # 2.1 Если это твое сообщение (userbot) и не команда - игнорируем (чтобы не зацикливать)
        if is_self and not text.startswith("/"):
            return

        # 2.2 Игнорируем сообщения от игнорируемых пользователей
        if sender and sender.lower() in command_handler.ignored_users:
            return

        text_lower = text.lower()

        # 3. Обработка команд из других чатов
        if text_lower.startswith("/help"):
            await command_handler.send_help(message)
            return
        if text_lower.startswith("/addword"):
            await command_handler.add_word(message)
            return
        if text.startswith("/delword"):  # новая команда для удаления ключевого слова
            await command_handler.del_word(message)
            return
        if text_lower.startswith("/игнор"):
            await command_handler.ignore_user(message)
            return
        if text.startswith("/неигнор"):  # новая команда для удаления пользователя из игнора
            await command_handler.unignore_user(message)
            return
        if text.startswith("/delchat"):
            await command_handler.del_chat(message)
            return
        if text_lower.startswith("/lasttime"):
            await command_handler.last_time(message)
            return
        if text.startswith("/hardscan"):
            await scheduler_loop()
            return

        # 4. Поиск ключевых слов в сообщениях из любых чатов (кроме своих исходящих)
        matched_keyword = next((k for k in command_handler.ALL_KEYWORDS if k in text_lower), None)
        if not matched_keyword:
            return

            # ПРОВЕРКА НА ИСКЛЮЧЕННЫЕ СЛОВОСОЧЕТАНИЯ
        if await contains_stopphrase(app, message.text):
            return

        time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chat_type = message.chat.type
        chat_title = message.chat.title if message.chat.title else f"Личка @{sender}" if sender else "Неизвестный чат"


        logging.info(f"Найдено слово: \"{matched_keyword}\" | Автор: @{sender} | Тип чата: {chat_type} | Чат: \"{chat_title}\"")

        link = get_message_link(message)
        await send_alert(app, message, matched_keyword, link=link)

    except Exception as e:
        await app.send_message(TARGET_CHAT, f"⚠️ Ошибка при обработке сообщения:\n`{str(e)}`")



class FakeMessage:
    def __init__(self, text, chat, from_user):
        self.text = text
        self.chat = chat
        self.from_user = from_user

    async def reply(self, text, **kwargs):
        return await app.send_message(self.chat.id, text, **kwargs)

@app.on_callback_query()
async def callback_ignore(client, callback_query):
    data = callback_query.data
    if data.startswith("ignore_"):
        username = data[len("ignore_"):]
        command_text = f"/ignore @{username}"

        fake_message = FakeMessage(
            text=command_text,
            chat=callback_query.message.chat,
            from_user=callback_query.from_user
        )

        await command_handler.ignore_user(fake_message)
        await callback_query.answer(f"Пользователь @{username} добавлен в игнор-лист.", show_alert=True)


async def scheduler_loop():
    logging.warning("шедулер за 30 минут по пропущенному:")
    await asyncio.sleep(10) #чутка ждем чтобы засинхрониться
    asyncio.create_task(alert_cache_cleaner(app))
    # await app.send_message(TARGET_CHAT, "⏰ Шедулер: запускаю дополнительное глубокое сканирование через получение истории.")
    last_morning_run_date = None  # чтобы запускать команду 1 раз в день утром

    while True:
        try:
            # Получаем текущее время по МСК
            now_moscow = datetime.datetime.now(MOSCOW_TZ)
            current_hour = now_moscow.hour
            current_date = now_moscow.date()


            # Утренний запуск команды /lasttime с динамическим аргументом
            if current_hour == START_HOUR and last_morning_run_date != current_date:
                # Вычисляем разницу в часах между END_HOUR и START_HOUR
                # Предполагается, что END_HOUR > START_HOUR, иначе можно добавить логику на переход через полночь
                hours_diff =  START_HOUR - END_HOUR
                if hours_diff <= 0:
                    hours_diff = 24 + hours_diff  # если переход через полночь

                class DummyMessage:
                    def __init__(self, hours):
                        self.text = f"/lasttime {hours}"
                        self.chat = type("Chat", (), {"id": TARGET_CHAT})()
                        self.from_user = None
                    async def reply(self, *a, **k): pass

                logging.warning(f"Утренний запуск /lasttime {hours_diff} в {now_moscow.strftime('%H:%M:%S')} МСК")
                await app.send_message(TARGET_CHAT, f"Утренний запуск /lasttime {hours_diff} в {now_moscow.strftime('%H:%M:%S')} МСК")
                await command_handler.last_time(DummyMessage(hours_diff))
                last_morning_run_date = current_date



            if START_HOUR <= current_hour < END_HOUR:
                class DummyMessage:
                    def __init__(self):
                        self.text = "/lasttime 1"
                        self.chat = type("Chat", (), {"id": TARGET_CHAT})()
                        self.from_user = None
                    async def reply(self, *a, **k): pass

                await command_handler.last_time(DummyMessage())
            else:
                logging.info(f"Сейчас {now_moscow.strftime('%H:%M:%S')} МСК — вне времени запуска, ждем.")

        except Exception as e:
            logging.warning(f"Ошибка в шедулере: {e}")
            await app.send_message(TARGET_CHAT, "автосканирование за прошлый час сломалось - включи вручную /hardscan")
        await asyncio.sleep(3600)  # 60 мин


async def send_startup_message_delayed():
    await asyncio.sleep(5)  # ждем, пока клиент подключится
    await send_startup_message(app)


async def init_dialogs(app):
    await asyncio.sleep(2)
    async for _ in app.get_dialogs():
        pass



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(init_dialogs(app))
    loop.create_task(send_startup_message_delayed())
    loop.create_task(scheduler_loop())  # <-- Запуск шедулера!
    logging.warning(f"БОТ ЗАПУЩЕН: от @{name_owner}")
    try:
        app.run()
    except KeyboardInterrupt:
        logging.warning("БОТ остановлен вручную:")
