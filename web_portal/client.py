from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False, index=True)
    passport_series = Column(String(4), nullable=False)
    passport_number = Column(String(6), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # НОВЫЕ ПОЛЯ для паспортных данных
    date_of_birth = Column(Date, nullable=True)
    passport_issue_date = Column(Date, nullable=True)
    passport_issue_place = Column(String(255), nullable=True)
    address = Column(String(500), nullable=True)

    # Связь с договорами аренды
    agreements = relationship("RentalAgreement", back_populates="client")