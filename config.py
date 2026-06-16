# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Поддержка переключения между SQLite и PostgreSQL через переменные окружения
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
if DB_TYPE == "postgresql":
    DB_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost:5432/rental_db")
else:
    # Относительный путь для SQLite, удобный для развертывания на Windows/Linux
    DB_URL = os.getenv("SQLITE_URL", "sqlite:///./rental.db")