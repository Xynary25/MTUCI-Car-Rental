from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class MaintenanceType(enum.Enum):
    """Типы технического обслуживания."""
    PLANNED = "Плановое ТО"
    UNSCHEDULED = "Внеплановое"
    SEASONAL = "Сезонное"
    REPAIR = "Ремонт"
    INSPECTION = "Осмотр"
    TIRE_CHANGE = "Замена шин"
    OIL_CHANGE = "Замена масла"
    OTHER = "Прочее"


class MaintenanceStatus(enum.Enum):
    """Статусы ТО."""
    SCHEDULED = "Запланировано"
    COMPLETED = "Выполнено"
    CANCELLED = "Отменено"
    IN_PROGRESS = "В процессе"


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    description = Column(Text, nullable=True)
    mileage = Column(Integer, nullable=True)  # Пробег в км
    next_mileage = Column(Integer, nullable=True)  # Следующее ТО на пробеге
    maintenance_date = Column(Date, nullable=False)
    next_maintenance_date = Column(Date, nullable=True)  # Дата следующего ТО
    cost = Column(Integer, nullable=True)  # Стоимость в рублях
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, nullable=False)
    performed_by = Column(String(100), nullable=True)  # Кто выполнял
    notes = Column(Text, nullable=True)  # Дополнительные заметки
    created_at = Column(Date, default=datetime.utcnow)

    # Связь с автомобилем
    car = relationship("Car", back_populates="maintenance_records")