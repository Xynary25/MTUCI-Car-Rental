from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
# ... внутри класса Client:
agreements = relationship("RentalAgreement", back_populates="client")
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False, index=True)
    passport_series = Column(String(4), nullable=False)
    passport_number = Column(String(6), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с договорами аренды (обратная связь будет добавлена в модели agreement)
    agreements = relationship("RentalAgreement", back_populates="client")