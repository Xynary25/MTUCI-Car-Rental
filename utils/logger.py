"""
Модуль логирования для системы AutoRent Pro.
Обеспечивает централизованное логирование всех событий.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = "CarRentalApp", log_file: str = None) -> logging.Logger:
    """
    Настройка и возврат конфигурированного логгера.

    Args:
        name: Имя логгера
        log_file: Путь к файлу логов (по умолчанию: logs/app.log)

    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Записываем всё, фильтруем на уровне handlers

    # Предотвращение дублирования логов при повторных вызовах
    if logger.handlers:
        return logger

    # Создание директории для логов, если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Формат сообщения
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s: %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Файловый логгер - ВСЕ уровни (DEBUG и выше)
    if log_file is None:
        log_file = log_dir / "app.log"
    else:
        log_file = Path(log_file)

    # Создаём файл если его нет
    log_file.parent.mkdir(parents=True, exist_ok=True)
    if not log_file.exists():
        log_file.touch()

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8',
        delay=True  # Отложенное создание файла
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Консольный логгер - только WARNING и выше
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 3. Отдельный файл для ошибок
    error_file = log_dir / "errors.log"
    if not error_file.exists():
        error_file.touch()

    error_handler = RotatingFileHandler(
        error_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding='utf-8',
        delay=True
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # 4. Отдельный файл для аудита действий пользователей
    audit_file = log_dir / "audit.log"
    if not audit_file.exists():
        audit_file.touch()

    audit_handler = RotatingFileHandler(
        audit_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
        delay=True
    )
    audit_handler.setLevel(logging.INFO)
    audit_formatter = logging.Formatter(
        '[%(asctime)s] AUDIT: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    audit_handler.setFormatter(audit_formatter)
    logger.addHandler(audit_handler)

    return logger


# Глобальный экземпляр логгера для импорта в другие модули
app_logger = setup_logger()


def log_user_action(user_id: int, username: str, action: str,
                    entity_type: str = None, entity_id: int = None,
                    details: str = None, ip_address: str = None):
    """
    Логирование действия пользователя (для аудита).

    Args:
        user_id: ID пользователя
        username: Логин пользователя
        action: Тип действия (CREATE, UPDATE, DELETE, LOGIN, LOGOUT и т.д.)
        entity_type: Тип сущности (Car, Client, Agreement и т.д.)
        entity_id: ID сущности
        details: Дополнительные детали
        ip_address: IP-адрес (если веб)
    """
    message = f"User: {username} (ID:{user_id}) | Action: {action}"

    if entity_type:
        message += f" | Entity: {entity_type}"
    if entity_id:
        message += f" (ID:{entity_id})"
    if details:
        message += f" | Details: {details}"
    if ip_address:
        message += f" | IP: {ip_address}"

    app_logger.info(f"AUDIT: {message}")


def log_error(module: str, error: Exception, context: str = None):
    """
    Логирование ошибки.

    Args:
        module: Имя модуля где произошла ошибка
        error: Объект исключения
        context: Дополнительный контекст
    """
    message = f"ERROR in {module}: {type(error).__name__}: {str(error)}"
    if context:
        message += f" | Context: {context}"

    app_logger.error(message, exc_info=True)


def log_database_action(action: str, table: str, record_id: int = None,
                        user: str = None, details: str = None):
    """
    Логирование действий с базой данных.

    Args:
        action: Действие (INSERT, UPDATE, DELETE)
        table: Имя таблицы
        record_id: ID записи
        user: Пользователь выполнивший действие
        details: Дополнительные детали
    """
    message = f"DB: {action} on {table}"
    if record_id:
        message += f" (ID:{record_id})"
    if user:
        message += f" by {user}"
    if details:
        message += f" | {details}"

    app_logger.info(f"DATABASE: {message}")


def log_security_event(event_type: str, username: str = None,
                       details: str = None, success: bool = True):
    """
    Логирование событий безопасности.

    Args:
        event_type: Тип события (LOGIN_ATTEMPT, LOGOUT, PASSWORD_CHANGE и т.д.)
        username: Имя пользователя
        details: Дополнительные детали
        success: Успешно ли событие
    """
    status = "SUCCESS" if success else "FAILED"
    message = f"SECURITY [{status}]: {event_type}"

    if username:
        message += f" | User: {username}"
    if details:
        message += f" | {details}"

    if success:
        app_logger.info(message)
    else:
        app_logger.warning(message)


def cleanup_old_logs(days: int = 30):
    """
    Очистка старых логов.

    Args:
        days: Удалять логи старше N дней
    """
    log_dir = Path("logs")
    if not log_dir.exists():
        return

    cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)

    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff_date:
            try:
                log_file.unlink()
                app_logger.info(f"Deleted old log file: {log_file.name}")
            except Exception as e:
                app_logger.error(f"Failed to delete {log_file.name}: {e}")


# Экспорт всех публичных функций
__all__ = [
    'app_logger',
    'setup_logger',
    'log_user_action',
    'log_error',
    'log_database_action',
    'log_security_event',
    'cleanup_old_logs'
]