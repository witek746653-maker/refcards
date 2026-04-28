import sqlite3, os

db_path = "refcards.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT content FROM cards WHERE id='43f9e2b1-1ab8-41fb-af16-2c649cb883b4'")
row = cursor.fetchone()
if row:
    print(row[0][:500])

conn.close()
