from sqlalchemy import func

from database import SessionLocal
from models.user import User
from models.client import Client

db = SessionLocal()

print("=" * 60)
print("📊 ПОЛЬЗОВАТЕЛИ:")
print("=" * 60)
users = db.query(User).all()
for u in users:
    print(f"ID: {u.id}, Логин: {u.username}, Роль: {u.role.value}, Email: {u.email}")

print("\n" + "=" * 60)
print("👥 КЛИЕНТЫ:")
print("=" * 60)
clients = db.query(Client).all()
for c in clients:
    print(f"ID: {c.id}, ФИО: {c.full_name}")
    print(f"  Паспорт: {c.passport_series} {c.passport_number}")
    print(f"  Телефон: {c.phone}")
    print(f"  Email: {c.email}")
    print()

print("\n" + "=" * 60)
print("🔍 ПРОВЕРКА ДУБЛИКАТОВ:")
print("=" * 60)

# Проверяем дубликаты телефонов
phones = db.query(Client.phone, func.count(Client.id)).group_by(Client.phone).having(func.count(Client.id) > 1).all()
if phones:
    print(f"❌ Найдены дубликаты телефонов: {phones}")
else:
    print("✅ Дубликатов телефонов нет")

# Проверяем дубликаты email
emails = db.query(Client.email, func.count(Client.id)).group_by(Client.email).having(func.count(Client.id) > 1).all()
if emails:
    print(f"❌ Найдены дубликаты email: {emails}")
else:
    print("✅ Дубликатов email нет")

db.close()