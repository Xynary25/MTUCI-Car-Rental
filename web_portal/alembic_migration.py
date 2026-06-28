"""Добавление дополнительных полей в таблицу clients."""
from sqlalchemy import create_engine, text
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "rental.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


def add_client_fields():
    """Добавляет новые поля в таблицу clients."""
    with engine.connect() as conn:
        # Проверяем существование колонок
        columns = conn.execute(text("PRAGMA table_info(clients)")).fetchall()
        column_names = [col[1] for col in columns]

        new_columns = [
            ("date_of_birth", "DATE"),
            ("passport_issue_date", "DATE"),
            ("passport_issue_place", "VARCHAR(255)"),
            ("passport_code", "VARCHAR(10)"),
            ("address", "VARCHAR(500)"),
            ("driver_license", "VARCHAR(50)")
        ]

        for col_name, col_type in new_columns:
            if col_name not in column_names:
                print(f"Добавляю колонку {col_name}...")
                conn.execute(text(f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}"))
                conn.commit()

        print("Миграция завершена!")


if __name__ == "__main__":
    add_client_fields()