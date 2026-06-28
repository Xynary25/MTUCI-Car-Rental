import os
import shutil
from datetime import datetime
from sqlalchemy.orm import Session
from models.audit_log import AuditLog, ActionType
from config import DB_URL
from utils import app_logger


def log_action(db: Session, action_type: ActionType, entity_name: str, description: str,
               entity_id: int = None, user_info: str = "Admin"):
    """Универсальная функция для записи действия в журнал аудита."""
    try:
        log_entry = AuditLog(
            action_type=action_type,
            entity_name=entity_name,
            entity_id=entity_id,
            description=description,
            user_info=user_info
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Ошибка записи в журнал аудита: {e}")


def create_database_backup(backup_dir: str, db_session: Session) -> dict:
    """Создание резервной копии SQLite базы данных."""
    if "sqlite" not in DB_URL:
        return {"success": False, "error": "Резервное копирование реализовано только для SQLite в данной версии."}

    # Извлекаем путь к файлу из строки подключения SQLAlchemy
    db_path = DB_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        return {"success": False, "error": "Файл базы данных не найден."}

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"rental_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        # Копирование файла с метаданными
        shutil.copy2(db_path, backup_path)

        # Фиксация действия в журнале аудита
        log_action(
            db=db_session,
            action_type=ActionType.BACKUP,
            entity_name="Database",
            description=f"Создана резервная копия: {backup_filename}",
            user_info="Admin"
        )
        return {"success": True, "path": backup_path}
    except Exception as e:
        return {"success": False, "error": f"Ошибка при копировании файла: {str(e)}"}


def cleanup_old_backups(backup_dir: str, max_backups: int = 10):
    """
    Удаление старых резервных копий, оставляя только max_backups последних.

    Args:
        backup_dir: Папка с бэкапами
        max_backups: Максимальное количество хранимых бэкапов (0 = без ограничений)
    """
    if max_backups <= 0:
        return

    if not os.path.exists(backup_dir):
        return

    # Получение списка файлов бэкапов
    backup_files = []
    for filename in os.listdir(backup_dir):
        if filename.startswith("rental_backup_") and filename.endswith(".db"):
            filepath = os.path.join(backup_dir, filename)
            backup_files.append({
                "path": filepath,
                "time": os.path.getmtime(filepath)
            })

    # Сортировка по времени создания (новые первые)
    backup_files.sort(key=lambda x: x["time"], reverse=True)

    if len(backup_files) > max_backups:
        for backup in backup_files[max_backups:]:
            try:
                os.remove(backup["path"])
                app_logger.info(f"Удален старый бэкап: {backup['path']}")
            except Exception as e:
                app_logger.error(f"Ошибка удаления бэкапа {backup['path']}: {str(e)}")