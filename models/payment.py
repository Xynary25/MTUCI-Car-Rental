from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class PaymentStatus(enum.Enum):
    PAID = "paid"
    PENDING = "pending"

class PaymentMethod(enum.Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey("rental_agreements.id"), nullable=False)
    amount = Column(Integer, nullable=False) # Сумма в рублях
    payment_date = Column(Date, nullable=False, default=datetime.utcnow().date)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PAID, nullable=False)

    agreement = relationship("RentalAgreement", back_populates="payments")