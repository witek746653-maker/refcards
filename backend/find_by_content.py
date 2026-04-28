import sqlite3, os

db_path = "refcards.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM cards WHERE content LIKE ?", ('%Comme Ils Disent%',))
rows = cursor.fetchall()
for row in rows:
    try:
        print(f"ID: {row[0]}, Name: {row[1]}")
    except:
        print(f"ID: {row[0]}, Name: [Encoding Error]")

conn.close()
