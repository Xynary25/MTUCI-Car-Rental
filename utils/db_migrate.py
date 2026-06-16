from sqlalchemy import create_engine, text
from config import DB_URL
import os


def migrate_database():
    """Добавление новых колонок в существующую таблицу cars."""
    if "sqlite" not in DB_URL:
        print("Миграции поддерживаются только для SQLite")
        return

    db_path = DB_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print("База данных не существует")
        return

    engine = create_engine(DB_URL)

    with engine.connect() as conn:
        # Проверка и добавление новых колонок
        columns_to_add = [
            ("cars", "year", "INTEGER"),
            ("cars", "transmission", "VARCHAR(20)"),
            ("cars", "fuel_type", "VARCHAR(20)"),
            ("cars", "engine_volume", "VARCHAR(10)"),
            ("cars", "color", "VARCHAR(30)"),
            ("cars", "image_path", "VARCHAR(255)"),
        ]

        for table, column, type_ in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {type_}"))
                print(f"Добавлена колонка {column} в таблицу {table}")
            except Exception as e:
                print(f"Колонка {column} уже существует или ошибка: {e}")

        conn.commit()
    print("Миграция завершена")


if __name__ == "__main__":
    migrate_database()