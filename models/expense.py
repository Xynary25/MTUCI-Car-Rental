from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class ExpenseType(enum.Enum):
    REPAIR = "Ремонт"
    FUEL = "Топливо"
    INSURANCE = "Страховка"
    OTHER = "Прочее"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=True)
    expense_type = Column(Enum(ExpenseType), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)
    date = Column(Date, default=datetime.utcnow, nullable=False)

    car = relationship("Car")