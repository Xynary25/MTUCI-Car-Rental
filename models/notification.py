from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    priority = Column(String(20), default='medium')
    is_read = Column(Boolean, default=False)
    agreement_id = Column(Integer, ForeignKey("rental_agreements.id"), nullable=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # НОВОЕ: привязка к пользователю
    created_at = Column(DateTime, default=datetime.utcnow)

    agreement = relationship("RentalAgreement")
    car = relationship("Car")
    user = relationship("User")  # НОВОЕ: связь с пользователем