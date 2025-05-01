#!/bin/bash
while true; do
    echo "Запуск бота..."
    python3 userbot.py
    echo "Бот упал с кодом $? - перезапуск через 5 секунд..."
    sleep 5
done
