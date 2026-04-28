import sqlite3, os

db_path = "refcards.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name, content FROM cards")
rows = cursor.fetchall()
for i, row in enumerate(rows):
    print(f"--- CARD {i} ---")
    print(f"Name: {row[0]}")
    print(f"Content length: {len(row[1])}")
    print(f"First 100 chars: {row[1][:100]}")

conn.close()
