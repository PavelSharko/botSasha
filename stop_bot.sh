#!/bin/bash
echo "Останавливаем бота..."

# Находим PID процесса userbot.py и убиваем
pkill -f "python3 userbot.py"

# Если запускаешь через run_bot.sh, убей и его
pkill -f "run_bot.sh"

echo "Бот остановлен."
