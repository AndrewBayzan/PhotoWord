import os

class Config:
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'SOME_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql+psycopg2://postgres:Forest1131213@localhost:5432/users_db')
    
    # Получаем строку подключения для второй базы данных
    words_db_uri = os.environ.get('WORDS_DATABASE_URI', 'postgresql+psycopg2://postgres:Forest1131213@localhost:5432/dictionarydb')
    
    # Настройка привязок для нескольких баз данных
    SQLALCHEMY_BINDS = {
        "words": words_db_uri
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False