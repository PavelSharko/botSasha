#!/bin/bash
LOG_LEVEL=${1:-INFO}  # если параметр не передан, по умолчанию INFO

while true; do
    echo "Запуск бота с уровнем логирования $LOG_LEVEL..."
    python3 userbot.py "$LOG_LEVEL"
    echo "Бот упал с кодом $? - перезапуск через 5 секунд..."
    sleep 5
done
