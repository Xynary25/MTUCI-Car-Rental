from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from database import Base
from datetime import datetime
import enum


class SupportRequestStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SupportRequest(Base):
    __tablename__ = "support_requests"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False)
    client_name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(SupportRequestStatus), default=SupportRequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_response = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)