"""
Модуль для передачи флага операции с БД между запусками приложения.
"""
import os
import json
import time

FLAG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db_operation_pending.json")


def set_db_operation_pending(operation: str = "manage"):
    """Установить флаг ожидающей операции с БД."""
    data = {
        "operation": operation,
        "timestamp": time.time()
    }
    try:
        with open(FLAG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Гарантируем запись на диск
        print(f"[FLAG] Флаг установлен: {FLAG_FILE}")
        print(f"[FLAG] Данные: {data}")
        return True
    except Exception as e:
        print(f"[FLAG] Ошибка установки флага: {e}")
        return False


def get_pending_operation() -> str | None:
    """Получить тип ожидающей операции. Возвращает None если флага нет."""
    try:
        if not os.path.exists(FLAG_FILE):
            print(f"[FLAG] Флаг не найден: {FLAG_FILE}")
            return None

        with open(FLAG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        operation = data.get("operation")
        print(f"[FLAG] Обнаружен флаг: {operation}")
        return operation
    except Exception as e:
        print(f"[FLAG] Ошибка чтения флага: {e}")
        return None


def clear_db_operation_flag():
    """Удалить флаг после выполнения операции."""
    try:
        if os.path.exists(FLAG_FILE):
            os.remove(FLAG_FILE)
            print(f"[FLAG] Флаг удален: {FLAG_FILE}")
        return True
    except Exception as e:
        print(f"[FLAG] Ошибка удаления флага: {e}")
        return False