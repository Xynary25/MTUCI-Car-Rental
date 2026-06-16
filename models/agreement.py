from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class AgreementStatus(enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RentalAgreement(Base):
    __tablename__ = "rental_agreements"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_cost = Column(Integer, nullable=False)
    status = Column(Enum(AgreementStatus), default=AgreementStatus.ACTIVE, nullable=False)

    # Связи с другими моделями
    client = relationship("Client", back_populates="agreements")
    car = relationship("Car", back_populates="agreements")
    payments = relationship("Payment", back_populates="agreement", cascade="all, delete-orphan")
    penalties = relationship("Penalty", back_populates="agreement", cascade="all, delete-orphan")