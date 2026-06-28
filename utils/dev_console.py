"""
Модуль логирования для разработки и отладки.
Записывает все действия системы в файл и консоль.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

# Создаем папку для логов
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Настраиваем логгер
dev_logger = logging.getLogger("dev_console")
dev_logger.setLevel(logging.DEBUG)

# Файловый обработчик
file_handler = logging.FileHandler(
    LOG_DIR / f"dev_{datetime.now().strftime('%Y%m%d')}.log",
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Формат
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

dev_logger.addHandler(file_handler)
dev_logger.addHandler(console_handler)


def log_support_request_action(action: str, request_id: int = None, details: str = ""):
    """Логирование действий с обращениями."""
    msg = f"[ОБРАЩЕНИЯ] {action}"
    if request_id:
        msg += f" ID={request_id}"
    if details:
        msg += f" | {details}"
    dev_logger.info(msg)


def log_db_query(query_type: str, table: str, details: str = ""):
    """Логирование запросов к БД."""
    msg = f"[БД] {query_type} из {table}"
    if details:
        msg += f" | {details}"
    dev_logger.debug(msg)


def log_status_change(entity: str, entity_id: int, old_status: str, new_status: str):
    """Логирование изменения статусов."""
    dev_logger.info(
        f"[СТАТУСЫ] {entity} ID={entity_id}: {old_status} -> {new_status}"
    )


def log_template_render(template_name: str, context_keys: list = None):
    """Логирование рендеринга шаблонов."""
    msg = f"[ШАБЛОНЫ] Рендеринг: {template_name}"
    if context_keys:
        msg += f" | Контекст: {', '.join(context_keys)}"
    dev_logger.debug(msg)


def log_enum_value(entity: str, field: str, value: str, value_type: str):
    """Логирование значений Enum для диагностики."""
    dev_logger.info(
        f"[ENUM] {entity}.{field} = '{value}' (type: {value_type})"
    )


def log_error(context: str, error: Exception, details: str = ""):
    """Логирование ошибок."""
    msg = f"[ОШИБКА] {context}: {str(error)}"
    if details:
        msg += f" | {details}"
    dev_logger.error(msg, exc_info=True)