import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "CarRentalApp") -> logging.Logger:
    """Настройка и возврат конфигурированного логгера."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Предотвращение дублирования логов при повторных вызовах
    if not logger.handlers:
        # Создание директории для логов, если её нет
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, "app.log")

        # Формат сообщения: [ДАТА ВРЕМЯ] УРОВЕНЬ: ИМЯ_МОДУЛЯ: СООБЩЕНИЕ
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(module)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # RotatingFileHandler ограничивает размер файла и хранит историю (maxBytes=5MB, backupCount=3)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Также выводим критические ошибки в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Глобальный экземпляр логгера для импорта в другие модули
app_logger = setup_logger()