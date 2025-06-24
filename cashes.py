# cashes.py

import asyncio
import os
import time
import logging

from bot_config import TARGET_CHAT

logger = logging.getLogger(__name__)

CACHE_FILE = "alerted_messages.txt"
CACHE_TTL_SECONDS = 24 * 60 * 60

class AlertCache:
    def __init__(self):
        self._set = set()
        self._load()
        self._last_clear = time.time()

    def _load(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                self._set = set(line.strip() for line in f if line.strip())

    def add(self, key):
        if key not in self._set:
            with open(CACHE_FILE, "a", encoding="utf-8") as f:
                f.write(key + "\n")
            self._set.add(key)

    def __contains__(self, key):
        return key in self._set

    def clear(self):
        self._set.clear()
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        self._last_clear = time.time()

alert_cache = AlertCache()

async def alert_cache_cleaner(app):

    while True:
        try:
            await asyncio.sleep(96 * 60 * 60)  # раз в  4 сутки
            alert_cache.clear()
            await app.send_message(TARGET_CHAT, "⏰ кэш сообщений почищен.")
            logger.warning("[AlertCache] Кеш очищен (раз в сутки)")
        except Exception as e:
            logger.error(f"[AlertCache] Ошибка при очистке кэша: {e}")

