from sqlalchemy.orm import Session
from models.agreement import RentalAgreement, AgreementStatus
from models.car import Car
from models.maintenance import Maintenance, MaintenanceStatus
from typing import List, Dict, Any
from datetime import date, timedelta


class CalendarController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_bookings_for_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Получение всех бронирований за период."""
        agreements = self.db.query(RentalAgreement).filter(
            RentalAgreement.start_date <= end_date,
            RentalAgreement.end_date >= start_date
        ).all()

        result = []
        for a in agreements:
            result.append({
                "id": a.id,
                "car_id": a.car_id,
                "car_info": f"{a.car.brand} {a.car.model} ({a.car.license_plate})",
                "client_name": a.client.full_name if a.client else "Неизвестно",
                "start_date": a.start_date,
                "end_date": a.end_date,
                "status": a.status.value,
                "total_cost": a.total_cost,
                "type": "agreement"  # Тип записи: договор
            })
        return result

    def get_maintenance_for_period(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Получение всех записей ТО за период."""
        records = self.db.query(Maintenance).filter(
            Maintenance.maintenance_date <= end_date,
            (Maintenance.next_maintenance_date >= start_date) | (Maintenance.next_maintenance_date.is_(None))
        ).all()

        result = []
        for m in records:
            # Для ТО используем maintenance_date как начало, next_maintenance_date как конец (если есть)
            m_start = m.maintenance_date
            m_end = m.next_maintenance_date if m.next_maintenance_date else m.maintenance_date

            result.append({
                "id": m.id,
                "car_id": m.car_id,
                "car_info": f"{m.car.brand} {m.car.model} ({m.car.license_plate})",
                "description": m.description or m.maintenance_type.value,
                "maintenance_type": m.maintenance_type.value,
                "start_date": m_start,
                "end_date": m_end,
                "status": m.status.value,
                "cost": m.cost,
                "performed_by": m.performed_by or "",
                "mileage": m.mileage,
                "type": "maintenance"  # Тип записи: ТО
            })
        return result

    def get_all_cars(self) -> List[Dict[str, Any]]:
        """Получение списка всех автомобилей."""
        cars = self.db.query(Car).all()
        return [
            {
                "id": c.id,
                "info": f"{c.brand} {c.model} ({c.license_plate})",
                "is_available": c.is_available
            }
            for c in cars
        ]

    def get_agreement_details(self, agreement_id: int) -> Dict[str, Any]:
        """Получение детальной информации о договоре."""
        agreement = self.db.query(RentalAgreement).filter(
            RentalAgreement.id == agreement_id
        ).first()
        if not agreement:
            return {}
        return {
            "id": agreement.id,
            "client": agreement.client.full_name if agreement.client else "Неизвестно",
            "car": f"{agreement.car.brand} {agreement.car.model} ({agreement.car.license_plate})",
            "start_date": agreement.start_date.strftime("%d.%m.%Y"),
            "end_date": agreement.end_date.strftime("%d.%m.%Y"),
            "status": agreement.status.value,
            "total_cost": agreement.total_cost,
            "days": (agreement.end_date - agreement.start_date).days
        }

    def get_maintenance_details(self, maintenance_id: int) -> Dict[str, Any]:
        """Получение детальной информации о ТО."""
        m = self.db.query(Maintenance).filter(
            Maintenance.id == maintenance_id
        ).first()
        if not m:
            return {}
        return {
            "id": m.id,
            "car": f"{m.car.brand} {m.car.model} ({m.car.license_plate})",
            "type": m.maintenance_type.value,
            "description": m.description or "Нет описания",
            "date": m.maintenance_date.strftime("%d.%m.%Y"),
            "next_date": m.next_maintenance_date.strftime("%d.%m.%Y") if m.next_maintenance_date else "Не запланировано",
            "mileage": f"{m.mileage} км" if m.mileage else "Не указан",
            "next_mileage": f"{m.next_mileage} км" if m.next_mileage else "Не указан",
            "cost": f"{m.cost} руб." if m.cost else "Не указана",
            "performed_by": m.performed_by or "Не указан",
            "status": m.status.value
        }