# from app import create_app
# app = create_app()
# print(repr(app.config["SQLALCHEMY_DATABASE_URI"]))

# import psycopg2
# conn = psycopg2.connect("postgresql://postgres:Forest1131213@localhost:5432/user_db")
# print("OK")
# conn.close()

# dsn = "postgresql://postgres:Forest1131213@localhost:5432/user_db"
# print(repr(dsn))
# print(list(dsn.encode("utf-8")))

import psycopg2

# DSN без проблем с кодировкой
dsn = "postgresql://postgres:Forest1131213@localhost:5432/users_db"

try:
    # Указываем client_encoding UTF8 и игнорируем lc_messages через options
    conn = psycopg2.connect(
        dsn,
        options='-c client_encoding=UTF8 -c lc_messages=C'
    )
    cur = conn.cursor()

    print("✅ Подключение успешно!\n")

    cur.execute("SELECT version();")
    print("Версия PostgreSQL:", cur.fetchone()[0])

    cur.close()
    conn.close()

except Exception as e:
    print("❌ Ошибка подключения:", e)