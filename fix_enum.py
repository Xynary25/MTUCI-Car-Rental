"""
Заменяет значения в нижнем регистре на верхний регистр (Enum).
"""
from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Показываем текущее состояние
    result = db.execute(text("""
        SELECT id, status, client_name 
        FROM support_requests
    """)).fetchall()

    print(f"\n📋 Найдено обращений: {len(result)}")
    for row in result:
        print(f"  Обращение #{row[0]}: статус='{row[1]}' - {row[2]}")

    updates = [
        ("in_progress", "IN_PROGRESS"),
        ("pending", "PENDING"),
        ("resolved", "RESOLVED"),
        ("closed", "CLOSED"),
    ]

    for old_val, new_val in updates:
        db.execute(text(f"""
            UPDATE support_requests 
            SET status = '{new_val}' 
            WHERE status = '{old_val}'
        """))
        print(f"  ✅ Обновлено: '{old_val}' -> '{new_val}'")

    db.commit()
    print("\n✅ Все статусы исправлены!")

    # Проверяем результат
    result = db.execute(text("""
        SELECT id, status, client_name 
        FROM support_requests
    """)).fetchall()

    print(f"\n📋 Проверка после исправления:")
    for row in result:
        print(f"  Обращение #{row[0]}: статус='{row[1]}' - {row[2]}")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    db.rollback()
finally:
    db.close()

print("\n" + "=" * 60)
print("🎯 Теперь перезапустите оба приложения!")
print("=" * 60)