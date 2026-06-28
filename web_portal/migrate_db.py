"""Простая инициализация БД."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import init_db

if __name__ == "__main__":
    print("🔧 Инициализация базы данных...")
    init_db()
    print("✅ Готово!")