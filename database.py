"""
Модуль работы с базой данных.
Централизованная настройка SQLAlchemy и инициализация БД.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from config import DB_URL
import logging

logger = logging.getLogger(__name__)

# Создание движка с параметрами безопасности и производительности
# echo=False отключает вывод SQL-запросов в консоль в продакшене (требование ИБ)
engine = create_engine(
    DB_URL,
    pool_size=20,  # было 10, увеличили до 20
    max_overflow=40,  # было 20, увеличили до 40
    pool_timeout=60,  # увеличили таймаут
    pool_recycle=1800,  # пересоздавать соединения каждые 30 минут
    pool_pre_ping=True,  # проверять соединение перед использованием
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Генератор сессий для безопасного управления транзакциями (FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Инициализация базы данных.
    Создаёт все таблицы если они не существуют.
    """
    from models.user import User, UserRole
    from models.car import Car
    from models.client import Client
    from models.agreement import RentalAgreement, AgreementStatus
    from models.payment import Payment
    from models.penalty import Penalty, PenaltyType, PenaltyStatus
    from models.maintenance import Maintenance
    from models.expense import Expense
    from models.audit_log import AuditLog, ActionType
    from models.return_request import ReturnRequest, ReturnRequestStatus
    from models.support_request import SupportRequest, SupportRequestStatus
    from models.support_message import SupportMessage
    from models.notification import Notification

    logger.info("Создание/проверка таблиц базы данных...")

    # Создаём все таблицы
    Base.metadata.create_all(bind=engine)

    logger.info("✅ Таблицы созданы/проверены")

    # Выводим список созданных таблиц для отладки
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"📋 Таблицы в БД: {tables}")

    return tables


def check_db_health():
    """Проверка здоровья БД."""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка проверки БД: {e}")
        return False


# Обработчик событий пула соединений для отладки
@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """Логирование создания соединений."""
    logger.debug("Создано новое соединение с БД")


@event.listens_for(engine, "checkout")
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    """Логирование получения соединений из пула."""
    logger.debug("Соединение получено из пула")


@event.listens_for(engine, "checkin")
def on_checkin(dbapi_connection, connection_record):
    """Логирование возврата соединений в пул."""
    logger.debug("Соединение возвращено в пул")