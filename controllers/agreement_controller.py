from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from models.agreement import RentalAgreement, AgreementStatus
from models.car import Car
from models.client import Client
from typing import List, Dict, Any, Optional
from datetime import date
from utils.system_utils import log_action
from models.audit_log import ActionType


class AgreementController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_agreements(self) -> List[Dict[str, Any]]:
        """Получение списка всех договоров с именами клиентов и марками авто."""
        agreements = self.db.query(RentalAgreement).join(Client).join(Car).all()
        result = []
        for a in agreements:
            result.append({
                "id": a.id,
                "client_name": a.client.full_name,
                "car_info": f"{a.car.brand} {a.car.model} ({a.car.license_plate})",
                "car_id": a.car_id,
                "start_date": a.start_date.strftime("%d.%m.%Y"),
                "end_date": a.end_date.strftime("%d.%m.%Y"),
                "total_cost": a.total_cost,
                "status": a.status.value
            })
        return result

    def check_car_availability(self, car_id: int, start_date: date, end_date: date) -> bool:
        """Проверка доступности автомобиля на заданные даты."""
        overlapping_agreement = self.db.query(RentalAgreement).filter(
            RentalAgreement.car_id == car_id,
            RentalAgreement.status == AgreementStatus.ACTIVE,
            and_(
                RentalAgreement.start_date <= end_date,
                RentalAgreement.end_date >= start_date
            )
        ).first()
        return overlapping_agreement is None

    def create_agreement(self, client_id: int, car_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Создание договора с проверкой пересечений."""
        if start_date >= end_date:
            return {"success": False, "error": "Дата окончания должна быть строго позже даты начала."}

        car = self.db.query(Car).filter(Car.id == car_id).first()
        if not car:
            return {"success": False, "error": "Выбранный автомобиль не найден."}

        if not car.is_available:
            return {"success": False, "error": "Автомобиль временно недоступен для аренды."}

        # ПРОВЕРКА: пересечение с другими договорами
        if not self.check_car_availability(car_id, start_date, end_date):
            return {"success": False, "error": "Автомобиль уже забронирован на выбранные даты."}

        # НОВАЯ ПРОВЕРКА: пересечение с записями ТО
        from models.maintenance import Maintenance, MaintenanceStatus
        from sqlalchemy import and_

        overlapping_maintenance = self.db.query(Maintenance).filter(
            Maintenance.car_id == car_id,
            Maintenance.status != MaintenanceStatus.CANCELLED,
            and_(
                Maintenance.maintenance_date <= end_date,
                (Maintenance.next_maintenance_date >= start_date) | (Maintenance.next_maintenance_date.is_(None))
            )
        ).first()

        if overlapping_maintenance:
            return {
                "success": False,
                "error": f"Автомобиль находится на ТО в этот период ({overlapping_maintenance.maintenance_type.value}). Перенесите даты или отмените ТО."
            }

        client = self.db.query(Client).filter(Client.id == client_id).first()
        days = (end_date - start_date).days
        total_cost = days * car.daily_rate

        new_agreement = RentalAgreement(
            client_id=client_id,
            car_id=car_id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost,
            status=AgreementStatus.ACTIVE
        )

        try:
            self.db.add(new_agreement)
            car.is_available = False
            self.db.commit()
            self.db.refresh(new_agreement)

            from utils.system_utils import log_action
            from models.audit_log import ActionType
            log_action(
                db=self.db,
                action_type=ActionType.CREATE,
                entity_name="Agreement",
                description=f"Создан договор аренды: {client.full_name} - {car.brand} {car.model} ({car.license_plate}) с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}",
                entity_id=new_agreement.id,
                user_info="Admin"
            )

            return {"success": True, "data": new_agreement}
        except IntegrityError:
            self.db.rollback()
            return {"success": False, "error": "Ошибка целостности данных при создании договора."}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Критическая ошибка БД: {str(e)}"}

    def complete_agreement(self, agreement_id: int) -> Dict[str, Any]:
        """Завершение договора и возврат автомобиля в статус 'доступен'."""
        agreement = self.db.query(RentalAgreement).filter(RentalAgreement.id == agreement_id).first()
        if not agreement:
            return {"success": False, "error": "Договор не найден."}

        if agreement.status != AgreementStatus.ACTIVE:
            return {"success": False, "error": "Договор уже завершен или отменен."}

        try:
            agreement.status = AgreementStatus.COMPLETED
            # Возвращаем доступность автомобилю
            car = self.db.query(Car).filter(Car.id == agreement.car_id).first()
            if car:
                car.is_available = True

            self.db.commit()

            # ЛОГИРОВАНИЕ: Завершение договора
            log_action(
                db=self.db,
                action_type=ActionType.UPDATE,
                entity_name="Agreement",
                description=f"Завершён договор аренды №{agreement_id}",
                entity_id=agreement_id,
                user_info="Admin"
            )

            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка при завершении договора: {str(e)}"}