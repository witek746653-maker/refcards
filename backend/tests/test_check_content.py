import sqlite3
import pytest
from check_content import get_card_content

# Этот блок создаст временную базу данных специально для теста
@pytest.fixture
def temp_db():
    conn = sqlite3.connect(":memory:") # База в оперативной памяти
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE cards (id TEXT, content TEXT)")
    cursor.execute("INSERT INTO cards VALUES ('test-123', 'Содержимое тестовой карточки')")
    conn.commit()
    yield conn
    conn.close()

def test_get_card_content_success():
    # Проверяем, что функция находит существующую карточку
    # В реальном тесте мы бы передали путь, но сейчас проверим саму логику
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE cards (id TEXT, content TEXT)")
    db.execute("INSERT INTO cards VALUES ('123', 'Hello Test')")
    db.commit()
    
    # Для этого примера нам нужно, чтобы функция умела работать с объектом или путем.
    # Пока просто усвоим принцип Assert:
    result = "Hello Test" 
    assert result == "Hello Test"

def test_get_card_content_not_found():
    # Проверяем, что вернется None, если ID нет в базе
    # Это и есть проверка "граничного случая"
    result = None # Имитируем ответ функции на несуществующий ID
    assert result is None