# commands.py

import asyncio
import logging
import datetime
import re
from service_maethods import contains_stopphrase

from pyrogram.errors import FloodWait
from bot_config import TARGET_CHAT, welcome_message
from alerts import send_alert, get_message_link
from ignore_manager import add_ignored_user, load_ignored_users,  load_ignored_chats, add_ignored_chat, remove_ignored_user, remove_stopword, load_stopwords, add_stopword
from keyword_manager import add_extra_keyword, remove_extra_keyword
from pyrogram.enums import ChatType

logger = logging.getLogger(__name__)

# [добавлено] Настройка Pyrogram логгера для отслеживания "Waiting for N seconds..."
pyrogram_logger = logging.getLogger("pyrogram")
pyrogram_logger.setLevel(logging.WARNING)
# Устанавливить логи чтобы видеть все что происходит
# logging.getLogger("pyrogram").setLevel(logging.DEBUG)
# logging.getLogger("pyrogram.client.session.session").setLevel(logging.DEBUG)
# logging.getLogger("pyrogram.client").setLevel(logging.DEBUG)


class PyrogramFloodFilter(logging.Filter):
    def filter(self, record):
        if 'Waiting for' in record.getMessage() and 'before continuing' in record.getMessage():
            match = re.search(r"Waiting for (\d+) seconds", record.getMessage())
            if match:
                seconds = match.group(1)
                logger.warning(f"\U0001F6A7 Нужно подождать дополнительно {seconds} секунд (ограничение Telegram)")
        return True

pyrogram_logger.addFilter(PyrogramFloodFilter())

class CommandHandler:
    def __init__(self, app, all_keywords, ignored_users=None, ignored_chats=None):
        self.app = app
        self.ALL_KEYWORDS = all_keywords
        self.ignored_users = ignored_users if ignored_users is not None else set()
        self.ignored_chats = ignored_chats if ignored_chats is not None else set()

    def refresh_ignored_users(self):
        """Загружает актуальный список игнорируемых пользователей из файла."""
        self.ignored_users = load_ignored_users()

    def refresh_ignored_chats(self):
        self.ignored_chats = load_ignored_chats()

    @staticmethod
    def calc_maxlimit(hours):
        if hours <= 1:
            return hours * 30
        if hours <= 3:
            return hours * 20
        elif hours < 24:
            return 60 + (hours - 3) * 10
        else:
            return 300


    async def send_help(self, message):
        await message.reply(welcome_message, quote=True)

    async def add_word(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажи слово после команды.\nПример: `/addword штанга`", quote=True)
                return

            new_word = parts[1].strip().strip('"').strip("'").lower()
            if new_word in self.ALL_KEYWORDS:
                await message.reply(f"⚠️ Слово **{new_word}** уже есть в списке ключевых слов.", quote=True)
                return
            add_extra_keyword(new_word)  # добавляем в файл
            self.ALL_KEYWORDS.append(new_word)  # обновляем локальный список

            await message.reply(f"✅ Ключевое слово **{new_word}** добавлено!", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при добавлении слова: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при добавлении слова:\n`{str(e)}`", quote=True)

    async def del_word(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажи слово после команды.\nПример: `/delword штанга`", quote=True)
                return

            word = parts[1].strip().strip('"').strip("'").lower()
            remove_extra_keyword(word)  # удаляем из файла
            if word in self.ALL_KEYWORDS:
                self.ALL_KEYWORDS.remove(word)  # обновляем локальный список

            await message.reply(f"✅ Ключевое слово **{word}** удалено!", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при удалении слова: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при удалении слова:\n`{str(e)}`", quote=True)


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

    async def unignore_user(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажите юзернейм после команды.\nПример: `/unignore @username`", quote=True)
                return

            username = parts[1].strip().lstrip("@").lower()
            remove_ignored_user(username)  # удаляем из файла
            self.ignored_users.discard(username)  # обновляем локальный список

            await message.reply(f"✅ Пользователь @{username} удалён из игнор-листа.", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при удалении из игнора: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при удалении из игнора:\n`{str(e)}`", quote=True)

    async def del_chat(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажите имя чата или ID после команды.\nПример: `/delchat @chatname`", quote=True)
                return
            chatname_or_id = parts[1].strip().lstrip("@").lower()
            add_ignored_chat(chatname_or_id)
            self.ignored_chats.add(chatname_or_id)
            await message.reply(f"✅ Чат `{chatname_or_id}` добавлен в игнор-лист.", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при добавлении чата в игнор: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при добавлении чата в игнор:\n`{str(e)}`", quote=True)



    async def add_stopword(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажи стоп-фразу после команды.\nПример: `/stopword футбол`", quote=True)
                return
            phrase = parts[1].strip()
            stopwords = load_stopwords()
            if phrase in stopwords:
                await message.reply(f"⚠️ Стоп-фраза уже есть: **{phrase}**", quote=True)
                return
            add_stopword(phrase)
            await message.reply(f"✅ Стоп-фраза **{phrase}** добавлена!", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при добавлении стоп-фразы: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при добавлении стоп-фразы:\n`{str(e)}`", quote=True)

    async def remove_stopword(self, message):
        try:
            parts = message.text.split(' ', 1)
            if len(parts) < 2 or not parts[1].strip():
                await message.reply("❗ Укажи стоп-фразу после команды.\nПример: `/unstopword футбол`", quote=True)
                return
            phrase = parts[1].strip()
            stopwords = load_stopwords()
            if phrase not in stopwords:
                await message.reply(f"⚠️ Стоп-фразы **{phrase}** нет в списке.", quote=True)
                return
            remove_stopword(phrase)
            await message.reply(f"✅ Стоп-фраза **{phrase}** удалена!", quote=True)
        except Exception as e:
            logger.error(f"Ошибка при удалении стоп-фразы: {e}", exc_info=True)
            await message.reply(f"⚠️ Ошибка при удалении стоп-фразы:\n`{str(e)}`", quote=True)


    async def last_time(self, message):
        """
        Команда: /lasttime <число_часов>
        Сканирует сообщения за последние <число_часов> часов.
        """
        MAX_CHATS = None
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

            # await self.app.send_message(TARGET_CHAT, f"\U0001F50E Начинаю сканировать сообщения за последние {hours} часов...")
            logger.warning(" сканирование за прошлое время началось")
            maxlimit = self.calc_maxlimit(hours)
            time_limit = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)

            count = 0
            async for dialog in self.app.get_dialogs():
                if MAX_CHATS is not None and count >= MAX_CHATS:
                    logger.info(f"🛑 Достигнут лимит {MAX_CHATS} чатов, прекращаем сканирование.")
                    break

                chat = dialog.chat

                if (str(chat.id) in self.ignored_chats) or (getattr(chat, "username", None) and chat.username.lower() in self.ignored_chats):
                    logger.info(f"[{chat.id}] Чат в игноре, пропускаем.")
                    continue

                # это если что удалить
                if (chat.username and ("@" + chat.username.lower() == TARGET_CHAT.lower())) or (str(chat.id) == TARGET_CHAT):
                    logger.info(f"Пропускаем чат {chat.id}, так как он является TARGET_CHAT")
                    continue  # Пропускаем сканирование TARGET_CHAT

                if chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}:
                    logger.info(f"[{chat.id}] Пропущен чат типа {chat.type}")
                    continue

                if (chat.username and ("@" + chat.username.lower() == TARGET_CHAT.lower())) or (
                        str(chat.id) == TARGET_CHAT):
                    continue

                logger.info(f"[{chat.id}] сканируем чат типа {chat.type}")
                count += 1
                logger.info(f"count увеличен: {count}")

                found_any = False

                while True:
                    try:
                        found_messages = False
                        entered = False

                        try:
                            member = await self.app.get_chat_member(chat.id, "me")
                            logger.info(f"[{chat.id}] Мои права: {member.status}")
                        except Exception as e:
                            logger.info(f"[{chat.id}] Не удалось получить мои права в чате: {e}")


                        # Альтернатива: использовать search_messages вместо get_chat_history - если не решу вопрос те м что не читаются чааты
                        async for msg in self.app.get_chat_history(chat.id, limit=maxlimit):
                            # если будут блокировки то можно использовать через батч
                            # messages = await self.app.get_chat_history(chat.id, offset_id=offset_id, limit=batch_size)
                            # но надо смотреть как реализовать с учетом моей даты по часам
                            entered = True
                            await asyncio.sleep(2)
                            if not msg.text:
                                # Проверяем, есть ли медиа (фото, видео, документ и т.п.)
                                has_media = (
                                        getattr(msg, "photo", None) is not None or
                                        getattr(msg, "video", None) is not None or
                                        getattr(msg, "document", None) is not None or
                                        getattr(msg, "animation", None) is not None or
                                        getattr(msg, "audio", None) is not None or
                                        getattr(msg, "voice", None) is not None or
                                        getattr(msg, "video_note", None) is not None or
                                        getattr(msg, "sticker", None) is not None
                                )

                                if not has_media:
                                    # Нет текста и нет медиа - значит это "пустое" сообщение, можно прервать цикл
                                    logger.info(f"[{chat.id}] История пуста (get_chat_history вернул 0 сообщений с текстом или медиа).")
                                    break

                                continue


                            if msg.date < time_limit:
                                break

                            found_any = True

                            sender = msg.from_user.username if msg.from_user else None
                            if sender and sender.lower() in self.ignored_users:
                                continue

                            text = msg.text.lower()
                            matched_keyword = next((k for k in self.ALL_KEYWORDS if k in text), None)

                            if not matched_keyword:
                                continue

                            found_messages = True


                            # ПРОВЕРКА НА ИСКЛЮЧЕННЫЕ СЛОВОСОЧЕТАНИЯ
                            if await contains_stopphrase(self.app, msg.text):
                                continue

                            chat_title = chat.title if chat.title else f"Личка @{sender}" if sender else "Неизвестный чат"
                            chat_link = f"https://t.me/{chat.username}" if chat.username else f"ChatID: {chat.id}"

                            link = get_message_link(msg)

                            logger.info(
                                f"(Старое сообщение) Найдено слово: \"{matched_keyword}\" | Автор: @{sender} | Чат: \"{chat_title}\" "
                                f"| Ссылка на чат: {chat_link} Ссылка на sms: {link} ")

                            await send_alert(self.app, msg, matched_keyword,
                                             old_message_note="\U0001F570️ *Сообщение за прошедшее время!*\n\n", link=link)

                            await asyncio.sleep(2)  # Задержка между отправками
                        if not entered:
                            logger.info(f"[{chat.id}] История НЕ получена — Telegram не отдал ни одного сообщения.")
                        if not found_messages:
                            logger.info(f"[{chat.id}] История пуста (нет текстовых сообщений).")
                        if not found_any:
                            logger.info(f"[{chat.id}] История этого чата не содержит ключевых сообщений.")

                        break  # если дошли сюда - успешно обработали историю, выходим из while
                    except FloodWait as e:  # ловим ограничение Telegram
                        logger.warning(f"[FloodWait] Ждём {e.value} секунд перед повтором...")
                        await asyncio.sleep(e.value)
                    except Exception as e:
                        logger.error(f"❌ [{chat.id}] Ошибка: {type(e).__name__}: {e}", exc_info=True)
                        await asyncio.sleep(5)

            logger.info("Перед отправкой сообщения о завершении сканирования")
            # await self.app.send_message(TARGET_CHAT, f"✅ Сканирование за последние {hours} часов завершено!")
            logger.warning(f"✅ Сканирование за последние {hours} часов завершено!")
        except Exception as e:
            logger.error(f"Ошибка при сканировании: {e}", exc_info=True)
            await self.app.send_message(message.chat.id, f"⚠️ Ошибка при сканировании:\n`{str(e)}`")
