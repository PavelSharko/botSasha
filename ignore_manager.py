# ignore_manager.py

import os
from bot_config import IGNORED_USERS_FILE, IGNORE_CHATS_FILE, STOPWORDS_FILE

def load_ignored_users():
    if not os.path.exists(IGNORED_USERS_FILE):
        open(IGNORED_USERS_FILE, "w", encoding="utf-8").close()
    with open(IGNORED_USERS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

def add_ignored_user(username):
    username = username.lower()
    users = load_ignored_users()
    if username not in users:
        with open(IGNORED_USERS_FILE, "a", encoding="utf-8") as f:
            f.write(username + "\n")


def load_ignored_chats():
    try:
        with open(IGNORE_CHATS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def add_ignored_chat(chatname_or_id):
    chatname_or_id = str(chatname_or_id).strip().lower()
    chats = load_ignored_chats()
    if chatname_or_id not in chats:
        with open(IGNORE_CHATS_FILE, "a", encoding="utf-8") as f:
            f.write(chatname_or_id + "\n")

def remove_ignored_user(username):
    username = username.lower()
    users = load_ignored_users()
    if username in users:
        users.remove(username)
        with open(IGNORED_USERS_FILE, "w", encoding="utf-8") as f:
            for u in users:
                f.write(u + "\n")


def load_stopwords():
    if not os.path.exists(STOPWORDS_FILE):
        open(STOPWORDS_FILE, "w", encoding="utf-8").close()
    with open(STOPWORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def add_stopword(phrase):
    phrase = phrase.strip()
    stopwords = load_stopwords()
    if phrase not in stopwords:
        with open(STOPWORDS_FILE, "a", encoding="utf-8") as f:
            f.write(phrase + "\n")

def remove_stopword(phrase):
    phrase = phrase.strip()
    stopwords = load_stopwords()
    if phrase in stopwords:
        stopwords.remove(phrase)
        with open(STOPWORDS_FILE, "w", encoding="utf-8") as f:
            for p in stopwords:
                f.write(p + "\n")