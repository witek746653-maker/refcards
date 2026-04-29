import sqlite3

# 1. Логика теперь в функции. Она принимает путь к БД и ID.
def get_card_content(db_path, card_id):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Используем ?, чтобы избежать SQL-инъекций (безопасность)
        cursor.execute("SELECT content FROM cards WHERE id=?", (card_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None

# 2. Этот блок сработает, только если ты запустишь файл напрямую
if __name__ == "__main__":
    target_id = '43f9e2b1-1ab8-41fb-af16-2c649cb883b4'
    content = get_card_content("refcards.db", target_id)
    if content:
        print(content[:500])
    else:
        print("Карточка не найдена")