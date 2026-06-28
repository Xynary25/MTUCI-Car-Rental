"""Создание таблицы notification_reads для существующей БД."""
from database import engine
from models.notification import NotificationRead
from sqlalchemy import inspect


def create_table_if_not_exists():
    """Создание таблицы если её нет."""
    inspector = inspect(engine)

    if 'notification_reads' not in inspector.get_table_names():
        print("🔧 Создание таблицы notification_reads...")
        NotificationRead.__table__.create(engine)
        print("✅ Таблица notification_reads создана!")
    else:
        print("✅ Таблица notification_reads уже существует")


if __name__ == "__main__":
    create_table_if_not_exists()