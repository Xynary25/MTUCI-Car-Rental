from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50), nullable=False, index=True)
    model = Column(String(50), nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    transmission = Column(String(20), nullable=False)
    fuel_type = Column(String(20), nullable=False)
    engine_volume = Column(String(10), nullable=True)
    engine_power = Column(Integer, nullable=True)
    color = Column(String(30), nullable=True)
    body_type = Column(String(30), nullable=True)
    seats = Column(Integer, nullable=True)
    image_path = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    is_available = Column(Boolean, default=True)
    daily_rate = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи с другими моделями
    agreements = relationship("RentalAgreement", back_populates="car")
    # Связь с записями ТО
    maintenance_records = relationship("Maintenance", back_populates="car", cascade="all, delete-orphan")