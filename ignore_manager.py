# ignore_manager.py

import os
from bot_config import IGNORED_USERS_FILE

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
