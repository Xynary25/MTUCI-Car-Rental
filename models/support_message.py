from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base
from datetime import datetime


class SupportMessage(Base):
    __tablename__ = "support_messages"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    support_request_id = Column(Integer, nullable=False)  # Убрали ForeignKey
    sender_type = Column(String(20), nullable=False)  # "client" или "admin"
    sender_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    attachment_path = Column(String(500), nullable=True)  # Путь к файлу
    created_at = Column(DateTime, default=datetime.utcnow)