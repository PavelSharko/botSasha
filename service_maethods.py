import re

import logging
logger = logging.getLogger(__name__)

from bot_config import TARGET_CHAT
from ignore_manager import   load_stopwords

async def contains_stopphrase(app, msg) -> bool:

    stopwords = load_stopwords()
    found_stopword = False
    logger.debug("\033[93mлогер 1 старт\033[0m")
    for stop in stopwords:
        logger.debug("\033[93mзашли в цикл проверки слов\033[0m")  # жёлтый
        if stop and matcher(msg, stop):
            logger.debug(f"\033[92mСообщение проигнорировано по стоп-фразе: {stop}\033[0m {msg}")  # зелёный
            # await app.send_message(TARGET_CHAT, f"Сообщение проигнорировано по стоп-фразе: {stop}")
            # logger.debug("\033[92mотправил в чат сообщение\033[0m")  # зелёный
            found_stopword = True
            return found_stopword
    logger.debug("\033[94mне может слово найти\033[0m")
    return found_stopword;


def matcher(text: str, stopphrase: str) -> bool:
    return stopphrase.strip().lower() in text.strip().lower()
