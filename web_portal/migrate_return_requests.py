"""Миграция для создания таблицы return_requests."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import engine
from return_request import ReturnRequest

def migrate():
    """Создание таблицы return_requests."""
    print(" Создание таблицы return_requests...")
    ReturnRequest.metadata.create_all(bind=engine)
    print("✅ Таблица return_requests создана!")

if __name__ == "__main__":
    migrate()