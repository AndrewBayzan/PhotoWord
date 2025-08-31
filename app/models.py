from .extensions import db
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import UniqueConstraint
from datetime import datetime

class Users(db.Model):
    __bind_key__ = None
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Words(db.Model):
    __bind_key__ = "words"
    __tablename__ = "words"
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, unique=True)
    transcription = db.Column(db.String(100))
    definition = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    audio_url = db.Column(db.String(200))
    cefr_level = db.Column(db.String(10))

class WrongWord(db.Model):
    __tablename__ = "wrong_words"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    word_id = db.Column(db.Integer, nullable=False)  # Убираем внешний ключ к words, так как это другая БД

    __table_args__ = (db.UniqueConstraint("user_id", "word_id", name="uq_wrong_words"),)
    