class Config:
    DEBUG = True
    SECRET_KEY = "SOME_KEY"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:Forest1131213@localhost:5432/users_db"
    
    SQLALCHEMY_BINDS = {
        "words": "postgresql+psycopg2://postgres:Forest1131213@localhost:5432/dictionarydb"
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False