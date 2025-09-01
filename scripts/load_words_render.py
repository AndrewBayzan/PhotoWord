#!/usr/bin/env python3
"""
Скрипт для загрузки данных в базу слов на Render
"""
import os
import sys
import csv
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# Получаем строку подключения из переменных окружения
words_db_uri = os.environ.get('WORDS_DATABASE_URI', 'postgresql+psycopg2://postgres:Forest1131213@localhost:5432/dictionarydb')

engine = create_engine(words_db_uri)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    word = Column(String(100), nullable=False, unique=True)
    transcription = Column(String(100))
    definition = Column(Text)
    image_url = Column(String(200))
    audio_url = Column(String(200))
    cefr_level = Column(String(10))

def create_tables():
    """Создает таблицы в базе данных"""
    Base.metadata.create_all(engine)
    print("Таблицы созданы успешно")

def load_sample_words():
    """Загружает примеры слов в базу данных"""
    sample_words = [
        "ball", "bicycle", "book", "bottle", "bridge", 
        "bus", "butterfly", "bed", "basket", "apple"
    ]
    
    for word in sample_words:
        try:
            new_word = Word(
                word=word,
                transcription=f"/{word}/",
                definition=f"A {word}",
                image_url=None,
                audio_url=None,
                cefr_level="A1"
            )
            session.add(new_word)
            session.commit()
            print(f"Слово '{word}' добавлено")
        except Exception as e:
            session.rollback()
            print(f"Слово {word} уже есть в БД или ошибка: {e}")

if __name__ == "__main__":
    print("Создание таблиц...")
    create_tables()
    
    print("Загрузка примеров слов...")
    load_sample_words()
    
    print("Загрузка завершена!")
