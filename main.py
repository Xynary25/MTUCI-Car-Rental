import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from database import engine, Base, SessionLocal
from models import car, client, agreement, payment, audit_log, expense, penalty, maintenance, user

import json
import threading
import logging
from pathlib import Path

# === НАСТРОЙКА ЛОГИРОВАНИЯ (на уровне модуля) ===
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info("🚀 Приложение AutoRent Pro запущено")
logger.info("=" * 60)

from utils.logger import app_logger, log_security_event
from utils.seeder import seed_database
from utils.backup_scheduler import backup_scheduler
from utils.auth_service import init_default_users
from views.login_dialog import LoginDialog

def monitor_pool():
    """Мониторинг пула соединений."""
    while True:
        try:
            pool = engine.pool
            print(f"Pool status: size={pool.size()}, checked_in={pool.checkedin()}, "
                  f"checked_out={pool.checkedout()}, overflow={pool.overflow()}")
        except Exception as e:
            print(f"Error monitoring pool: {e}")
        threading.Event().wait(10)  # Каждые 10 секунд

def load_settings() -> dict:
    """Загрузка настроек приложения."""
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "theme": "light",
        "font_size": 13,
        "db_type": "sqlite",
        "backup_path": "./backups",
        "auto_backup": True,
        "auto_backup_frequency": "daily",
        "auto_backup_hour": 23,
        "auto_backup_minute": 0,
        "auto_backup_day": 0,
        "max_backups": 10,
        "email_notifications": False
    }


def init_database():
    """Инициализация базы данных."""
    try:
        # Используем централизованную функцию из database.py
        from database import init_db
        tables = init_db()

        app_logger.info(f"✅ Таблицы созданы/проверены: {len(tables)} таблиц")

        db_session = SessionLocal()
        try:
            # Создание тестовых пользователей
            init_default_users(db_session)
            app_logger.info("Тестовые пользователи созданы/проверены")

            # Создание тестовых данных (автомобили, клиенты и т.д.)
            from utils.seeder import seed_database
            seed_database(db_session)
            app_logger.info("Тестовые данные созданы")

        finally:
            db_session.close()

    except Exception as e:
        app_logger.critical(f" Ошибка инициализации БД: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def start_backup_scheduler(settings: dict):
    """Запуск планировщика бэкапов если включен."""
    if settings.get("auto_backup", False):
        backup_dir = settings.get("backup_path", "./backups")
        frequency = settings.get("auto_backup_frequency", "daily")
        hour = settings.get("auto_backup_hour", 23)
        minute = settings.get("auto_backup_minute", 0)
        day = settings.get("auto_backup_day", 0)

        success = backup_scheduler.start(
            backup_dir=backup_dir,
            frequency=frequency,
            hour=hour,
            minute=minute,
            day_of_week=day
        )

        if success:
            app_logger.info("Автоматическое резервное копирование активировано")
        else:
            app_logger.error("Не удалось запустить планировщик бэкапов")


def main():
    """Главная функция запуска приложения."""

    def handle_exception(exc_type, exc_value, exc_traceback):
        app_logger.critical("Необработанное исключение", exc_info=(exc_type, exc_value, exc_traceback))
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        if QApplication.instance() is not None:
            QMessageBox.critical(None, "Критическая ошибка",
                                 f"Произошла непредвиденная ошибка:\n\n{exc_value}\n\n"
                                 f"Подробности в файле logs/app.log")

    sys.excepthook = handle_exception

    try:
        app_logger.info("=" * 50)
        app_logger.info("Запуск AutoRent Pro v1.0")
        app_logger.info("=" * 50)

        app = QApplication(sys.argv)
        app.setApplicationName("AutoRent Pro")
        app.setOrganizationName("MTUCI")
        app.setApplicationVersion("1.0.0")

        # Загрузка настроек
        settings = load_settings()

        # Инициализация БД
        init_database()

        # Запуск планировщика бэкапов
        start_backup_scheduler(settings)

        # Показываем диалог входа
        login_dialog = LoginDialog()
        if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
            app_logger.info("Пользователь отменил вход")
            if backup_scheduler.is_running:
                backup_scheduler.stop()
            sys.exit(0)

        current_user = login_dialog.get_user()
        if not current_user:
            app_logger.error("Не удалось получить данные пользователя")
            if backup_scheduler.is_running:
                backup_scheduler.stop()
            sys.exit(1)

        app_logger.info(f"Пользователь {current_user.username} ({current_user.role.value}) вошёл в систему")

        # Импорт и показ главного окна
        from views.main_window import MainWindow
        window = MainWindow(current_user=current_user)
        window.show()

        app_logger.info("Главное окно отображено")
        app_logger.info("Приложение готово к работе!")

        # Запуск event loop Qt
        exit_code = app.exec()

        # Остановка планировщика перед выходом
        if backup_scheduler.is_running:
            backup_scheduler.stop()

        sys.exit(exit_code)

    except Exception as e:
        app_logger.critical(f"Ошибка запуска приложения: {str(e)}")
        if QApplication.instance() is not None:
            QMessageBox.critical(None, "Ошибка запуска",
                                 f"Не удалось запустить приложение:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()