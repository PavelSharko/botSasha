# commands.py

import asyncio
import logging
import datetime

from bot_config import TARGET_CHAT
from alerts import send_alert, get_message_link
from ignore_manager import add_ignored_user, load_ignored_users
from keyword_manager import add_extra_keyword

logger = logging.getLogger(__name__)




class CommandHandler:
    def __init__(self, app, all_keywords, ignored_users=None):
        self.app = app
        self.ALL_KEYWORDS = all_keywords
        self.ignored_users = ignored_users if ignored_users is not None else set()

    def refresh_ignored_users(self):
        """Загружает актуальный список игнорируемых пользователей из файла."""
        self.ignored_users = load_ignored_users()

    async def send_help(self, message):
        help_text = (
            "🛠️ **Доступные команды:**\n\n"
            "/addword \"слово\" - добавить новое ключевое слово\n"
            "/ignore \"@username\" - добавить пользователя в игнор-лист\n"
            "/lasttime <часы> - вручную просканировать чаты за последние часы\n"
            "/help - показать это сообщение\n\n"
            "‼️ Пиши команды в любом месте (Избранное, группы, ЛС)."
        )
        await message.reply(help_text, quote=True)

    async def add_word(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажи слово после команды.\nПример: `/addword штанга`", quote=True)
                return

            new_word = parts[1].strip().strip('"').strip("'").lower()
            add_extra_keyword(new_word)  # добавляем в файл
            self.ALL_KEYWORDS.append(new_word)  # обновляем локальный список

            await message.reply(f"✅ Ключевое слово **{new_word}** добавлено!", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при добавлении слова: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при добавлении слова:\n`{str(e)}`", quote=True)

    async def ignore_user(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажите юзернейм после команды.\nПример: `/ignore @username`", quote=True)
                return

            username = parts[1].strip().lstrip("@").lower()
            add_ignored_user(username)  # добавляем в файл
            self.ignored_users.add(username)  # обновляем локальный список

            await message.reply(f"✅ Пользователь @{username} добавлен в игнор-лист.", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при добавлении в игнор: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при добавлении в игнор:\n`{str(e)}`", quote=True)

    async def last_time(self, message):
        """
        Команда: /lasttime <число_часов>
        Сканирует сообщения за последние <число_часов> часов.
        """
        try:
            self.refresh_ignored_users()

            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажите количество часов после команды.\nПример: `/lasttime 24`", quote=True)
                return

            try:
                hours = int(parts[1].strip())
                if hours <= 0:
                    raise ValueError()
            except ValueError:
                await message.reply(
                    "❗ Некорректное число часов. Укажите положительное целое число.\nПример: `/lasttime 24`",
                    quote=True)
                return

            await message.reply(f"🔎 Начинаю сканировать сообщения за последние {hours} часов...")

            time_limit = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)

            async for dialog in self.app.get_dialogs():
                chat = dialog.chat

                if (chat.username and ("@" + chat.username.lower() == TARGET_CHAT.lower())) or (
                        str(chat.id) == TARGET_CHAT):
                    continue

                async for msg in self.app.get_chat_history(chat.id, limit=100):
                    if not msg.text:
                        continue
                    if msg.date < time_limit:
                        break

                    sender = msg.from_user.username if msg.from_user else None
                    if sender and sender.lower() in self.ignored_users:
                        continue

                    text = msg.text.lower()
                    matched_keyword = next((k for k in self.ALL_KEYWORDS if k in text), None)

                    if not matched_keyword:
                        continue

                    chat_title = chat.title if chat.title else f"Личка @{sender}" if sender else "Неизвестный чат"
                    chat_link = f"https://t.me/{chat.username}" if chat.username else f"ChatID: {chat.id}"  # ссылка или id

                    link = get_message_link(msg)

                    logger.info(
                        f"(Старое сообщение) Найдено слово: \"{matched_keyword}\" | Автор: @{sender} | Чат: \"{chat_title}\" "
                        f"| Ссылка на чат: {chat_link} Ссылка на sms: {link} ")


                    await send_alert(self.app, msg, matched_keyword,
                                     old_message_note="🕰️ *Сообщение за прошедшее время!*\n\n", link=link)

                    await asyncio.sleep(5)  # Задержка между отправками

            await message.reply(f"✅ Сканирование за последние {hours} часов завершено!")
        except Exception as e:
            logger.error(f"Ошибка при сканировании: {e}", exc_info=True)
            await self.app.send_message(message.chat.id, f"⚠️ Ошибка при сканировании:\n`{str(e)}`")
