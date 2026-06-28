from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class ReturnRequestStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    rental_id = Column(Integer, nullable=False)
    client_id = Column(Integer, nullable=False)
    car_id = Column(Integer, nullable=False)

    request_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(ReturnRequestStatus), default=ReturnRequestStatus.PENDING, nullable=False)

    client_name = Column(String(100), nullable=False)
    car_info = Column(String(100), nullable=False)
    rental_period = Column(String(50), nullable=False)

    admin_decision_date = Column(DateTime, nullable=True)
    admin_comment = Column(String(255), nullable=True)