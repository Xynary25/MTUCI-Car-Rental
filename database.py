# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

# Создание движка с параметрами безопасности и производительности
# echo=False отключает вывод SQL-запросов в консоль в продакшене (требование ИБ)
engine = create_engine(
    DB_URL,
    pool_size=20,           # было 10, увеличили до 20
    max_overflow=40,        # было 20, увеличили до 40
    pool_timeout=60,        # увеличили таймаут
    pool_recycle=1800,      # пересоздавать соединения каждые 30 минут
    pool_pre_ping=True,      # проверять соединение перед использованием
    echo=False, connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Генератор сессий для безопасного управления транзакциями."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()