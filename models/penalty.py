from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class PenaltyType(enum.Enum):
    """Типы штрафов и дополнительных платежей."""
    FINE = "Штраф ПДД"
    DAMAGE = "Повреждение авто"
    CLEANING = "Мойка"
    REFUELING = "Неполная заправка"
    LATE_RETURN = "Просрочка возврата"
    SMOKING = "Курение в салоне"
    LOST_KEY = "Потеря ключей"
    OTHER = "Прочее"


class PenaltyStatus(enum.Enum):
    """Статус оплаты штрафа."""
    PENDING = "Не оплачен"
    PAID = "Оплачен"
    CANCELLED = "Отменён"


class Penalty(Base):
    __tablename__ = "penalties"

    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey("rental_agreements.id"), nullable=False)
    penalty_type = Column(Enum(PenaltyType), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)
    date = Column(Date, default=datetime.utcnow, nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    status = Column(Enum(PenaltyStatus), default=PenaltyStatus.PENDING, nullable=False)
    created_at = Column(Date, default=datetime.utcnow)

    # Связь с договором
    agreement = relationship("RentalAgreement", back_populates="penalties")