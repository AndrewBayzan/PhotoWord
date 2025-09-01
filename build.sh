#!/bin/bash

# Установка зависимостей
pip install -r requirements.txt

# Инициализация миграций для основной базы данных
flask db init || true
flask db migrate -m "Initial migration" || true
flask db upgrade || true

# Инициализация миграций для базы данных слов
flask db init --multidb || true
flask db migrate -m "Words database migration" --multidb || true
flask db upgrade --multidb || true

# Загрузка данных в базу слов
python scripts/load_words_render.py || true

echo "Build completed successfully!"

