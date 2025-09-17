import requests
import csv
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:Forest1131213@localhost:5432/dictionarydb")
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

Base.metadata.create_all(engine)



UNSPLASH_KEY = "GFaULAGMuN3r9d_eds-NtDq1xpNYWSKrSDwjx29xWvI"

def load_cefr_dict(csv_path="b:/PhotoWord/scripts/ENGLISH_CERF_WORDS.csv"):
    cefr = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cefr[row["headword"].lower()] = row["CEFR"].upper()
    return cefr

cefr_dict = load_cefr_dict("b:/PhotoWord/scripts/ENGLISH_CERF_WORDS.csv")

def get_word_data(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    r = requests.get(url).json()
    try:
        transcription = r[0].get("phonetics", [{}])[0].get("text", "")
        definition = r[0]["meanings"][0]["definitions"][0]["definition"]
        audio_url = next((p.get("audio") for p in r[0].get("phonetics", []) if p.get("audio")), None)
        return transcription, definition, audio_url
    except Exception as e:
        print(f"Ошибка при получении данных для слова {word}: {e}")
        return "", "", None
    
def get_image_url(word):
    url =  f"https://api.unsplash.com/search/photos?query={word}&per_page=1&client_id={UNSPLASH_KEY}"
    r = requests.get(url).json()
    if r.get("results"):
      return r["results"][0]["urls"]["regular"]
    return None


       

def add_word(word):
    transcription, definition, audio_url = get_word_data(word)
    image_url = get_image_url(word)
    cefr_level = cefr_dict.get(word.lower(), "A1")

    new_word = Word(
        word=word,
        transcription=transcription,
        definition=definition,
        image_url=image_url,
        audio_url=audio_url,
        cefr_level=cefr_level
    )
    session.add(new_word)
    try:
        session.commit()
        print(f"Слово '{word}' добавлено")
    except Exception:
        session.rollback()
        print(f"Слово {word} уже есть в БД")

for w in [
    "ball",
    "bicycle",
    "book",
    "bottle",
    "bridge",
    "bus",
    "butterfly",
    "bed",
    "basket"
]:
    add_word(w)