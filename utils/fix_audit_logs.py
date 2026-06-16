from database import SessionLocal, engine
from models.audit_log import AuditLog, ActionType
from sqlalchemy import text

def fix_audit_logs():
    """Исправление записей в журнале аудита."""
    db = SessionLocal()
    try:
        # Удаляем все записи с некорректными action_type
        db.execute(text("DELETE FROM audit_logs WHERE action_type NOT IN ('CREATE', 'UPDATE', 'DELETE', 'BACKUP', 'EXPORT', 'AUTH', 'LOGIN', 'LOGOUT', 'LOGIN_FAILED')"))
        db.commit()
        print("Журнал аудита очищен от некорректных записей")
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_audit_logs()