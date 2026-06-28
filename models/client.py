from sqlalchemy import Column, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    passport_series = Column(String(10), nullable=False)
    passport_number = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    date_of_birth = Column(Date, nullable=True)

    # ✅ ЭТИ ПОЛЯ ДОЛЖНЫ БЫТЬ
    passport_issue_date = Column(Date, nullable=True)
    passport_issue_place = Column(String(200), nullable=True)
    address = Column(String(300), nullable=True)

    # Связь с договорами аренды
    agreements = relationship("RentalAgreement", back_populates="client")