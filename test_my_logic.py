# Тестируемая функция (обычно она в другом файле, но для первого раза напишем здесь)
def format_card_name(name):
    return name.strip().upper()

# Сам тест
def test_format_card_name():
    # Arrange: исходное имя с пробелами и в разном регистре
    raw_name = "  history card  "
    expected = "HISTORY CARD"
    
    # Act: выполняем форматирование
    result = format_card_name(raw_name)
    
    # Assert: проверяем результат
    assert result == expected, f"Ожидали {expected}, но получили {result}"