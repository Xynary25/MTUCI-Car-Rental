from sqlalchemy import Column, Integer, String, DateTime, Enum
from database import Base
from datetime import datetime
import enum


class ActionType(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    BACKUP = "BACKUP"
    EXPORT = "EXPORT"
    AUTH = "AUTH"  # ДОБАВЛЕНО: для логирования входа/выхода
    LOGIN = "LOGIN"  # ДОБАВЛЕНО: успешный вход
    LOGOUT = "LOGOUT"  # ДОБАВЛЕНО: выход из системы
    LOGIN_FAILED = "LOGIN_FAILED"  # ДОБАВЛЕНО: неудачный вход


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action_type = Column(Enum(ActionType), nullable=False)
    entity_name = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=True)
    description = Column(String(255), nullable=False)
    user_info = Column(String(100), default="System")