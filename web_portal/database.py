"""
Конфигурация подключения к базе данных для веб-портала.
Подключается к той же БД, что и десктопная СУ (rental.db в корне проекта).
"""
import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь, чтобы найти config.py
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DB_URL

# Используем абсолютный путь к БД в корне проекта
# Если DB_URL относительный (sqlite:///./rental.db), заменяем на абсолютный
if DB_URL.startswith("sqlite:///./"):
    # Извлекаем имя файла БД
    db_filename = DB_URL.replace("sqlite:///./", "")
    # Создаём абсолютный путь к БД в корне проекта
    DB_PATH = PROJECT_ROOT / db_filename
    DB_URL = f"sqlite:///{DB_PATH}"
    print(f"✅ Подключение к БД: {DB_PATH}")
elif DB_URL.startswith("sqlite:///"):
    # Относительный путь без ./
    db_filename = DB_URL.replace("sqlite:///", "")
    DB_PATH = PROJECT_ROOT / db_filename
    DB_URL = f"sqlite:///{DB_PATH}"
    print(f"✅ Подключение к БД: {DB_PATH}")
else:
    print(f"✅ Используем БД: {DB_URL}")


# Создание движка с параметрами безопасности и производительности
engine = create_engine(
    DB_URL,
    pool_size=20,
    max_overflow=40,
    pool_timeout=60,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in DB_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Генератор сессий для безопасного управления транзакциями."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Проверка подключения к БД и создание таблиц если их нет.
    НЕ создаёт тестовые данные - они берутся из десктопной СУ.
    """
    # ✅ ИМПОРТИРУЕМ ВСЕ МОДЕЛИ (из web_models и из models/)
    from web_models import Car, Client, RentalAgreement, Penalty, User
    from models.support_request import SupportRequest, SupportRequestStatus
    from models.support_message import SupportMessage
    from models.notification import Notification, NotificationRead
    from models.return_request import ReturnRequest, ReturnRequestStatus
    from models.audit_log import AuditLog, ActionType

    # Проверяем подключение к БД
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print(f"✅ Подключение к БД установлено")
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        raise

    # Создаём таблицы если их нет (это безопасно - если таблицы есть, ничего не произойдёт)
    print("🔧 Проверка/создание таблиц...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы/проверены")

    # Проверяем существующие таблицы
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"📋 Таблицы в БД: {tables}")

    # Миграция: добавляем новые поля в clients если их нет
    if 'clients' in tables:
        columns = inspector.get_columns('clients')
        column_names = [col['name'] for col in columns]
        print(f"📋 Колонки таблицы clients: {column_names}")

        new_columns = {
            'date_of_birth': 'DATE',
            'passport_issue_date': 'DATE',
            'passport_issue_place': 'VARCHAR(255)',
            'address': 'VARCHAR(500)',
        }

        with engine.connect() as conn:
            for col_name, col_type in new_columns.items():
                if col_name not in column_names:
                    print(f"➕ Добавляю колонку {col_name}...")
                    try:
                        conn.execute(text(
                            f"ALTER TABLE clients ADD COLUMN {col_name} {col_type}"
                        ))
                        conn.commit()
                        print(f"   ✅ Колонка {col_name} добавлена")
                    except Exception as e:
                        print(f"   ⚠️ Ошибка при добавлении {col_name}: {e}")
    else:
        print("⚠️ Таблица clients не найдена - будет создана")

    # Проверяем количество данных ТОЛЬКО если таблицы существуют
    db = SessionLocal()
    try:
        if 'cars' in tables:
            car_count = db.query(Car).count()
            print(f"🚗 Автомобилей в БД: {car_count}")

            if car_count == 0:
                print("️ Автопарк пуст - запустите десктопную СУ для создания тестовых данных")
        else:
            print("⚠️ Таблица cars не найдена")

        if 'users' in tables:
            user_count = db.query(User).count()
            print(f"👥 Пользователей в БД: {user_count}")

            if user_count == 0:
                print("️ Нет пользователей - запустите десктопную СУ для создания админов")
        else:
            print("⚠️ Таблица users не найдена")

        # Проверяем таблицы обращений и уведомлений
        if 'support_requests' in tables:
            support_count = db.query(SupportRequest).count()
            print(f"📩 Обращений в поддержку: {support_count}")
        else:
            print("⚠️ Таблица support_requests не найдена")

        if 'notifications' in tables:
            notif_count = db.query(Notification).count()
            print(f"🔔 Уведомлений: {notif_count}")
        else:
            print("⚠️ Таблица notifications не найдена")

        if 'return_requests' in tables:
            return_count = db.query(ReturnRequest).count()
            print(f"🔄 Запросов на возврат: {return_count}")
        else:
            print("⚠️ Таблица return_requests не найдена")

        if 'notification_reads' in tables:
            print("✅ Таблица notification_reads существует (индивидуальное прочтение)")
        else:
            print("⚠️ Таблица notification_reads не найдена - уведомления будут общими")

    except Exception as e:
        print(f"⚠️ Ошибка при проверке данных: {e}")
    finally:
        db.close()