import psycopg2

conn = psycopg2.connect(
    dbname="users_db",
    user="postgres",
    password="Forest1131213",
    host="localhost",
    port="5432"
)
cur = conn.cursor()
cur.execute("SELECT 1")
print(cur.fetchone())
conn.close()