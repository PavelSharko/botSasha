# keyword_manager.py

import os
from bot_config import EXTRA_KEYWORDS_FILE, KEYWORDS, TRAINER_KEYWORDS

def load_extra_keywords():
    if not os.path.exists(EXTRA_KEYWORDS_FILE):
        open(EXTRA_KEYWORDS_FILE, "w", encoding="utf-8").close()
    with open(EXTRA_KEYWORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

def add_extra_keyword(word):
    word = word.lower()
    with open(EXTRA_KEYWORDS_FILE, "a", encoding="utf-8") as f:
        f.write(word + "\n")

def get_all_keywords():
    extra_keywords = load_extra_keywords()
    return [w.lower() for w in KEYWORDS + TRAINER_KEYWORDS] + extra_keywords

def remove_extra_keyword(word):
    word = word.lower()
    words = load_extra_keywords()
    if word in words:
        words.remove(word)
        with open(EXTRA_KEYWORDS_FILE, "w", encoding="utf-8") as f:
            for w in words:
                f.write(w + "\n")
