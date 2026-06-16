from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func as sa_func
from models.maintenance import Maintenance, MaintenanceType, MaintenanceStatus
from models.car import Car
from typing import List, Dict, Any
from datetime import date, timedelta


class MaintenanceController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_maintenance(self) -> List[Dict[str, Any]]:
        """Получение списка всех записей ТО."""
        records = (
            self.db.query(Maintenance)
            .join(Car)
            .order_by(Maintenance.maintenance_date.desc())
            .all()
        )
        result = []
        for m in records:
            result.append({
                "id": m.id,
                "car_id": m.car_id,
                "car_info": f"{m.car.brand} {m.car.model} ({m.car.license_plate})",
                "maintenance_type": m.maintenance_type.value,
                "description": m.description or "",
                "mileage": m.mileage,
                "next_mileage": m.next_mileage,
                "maintenance_date": m.maintenance_date.strftime("%d.%m.%Y"),
                "next_maintenance_date": m.next_maintenance_date.strftime(
                    "%d.%m.%Y") if m.next_maintenance_date else None,
                "cost": m.cost,
                "status": m.status.value,
                "performed_by": m.performed_by or "",
                "notes": m.notes or ""
            })
        return result

    def get_upcoming_maintenance(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Получение приближающихся ТО (в течение days_ahead дней)."""
        today = date.today()
        future_date = today + timedelta(days=days_ahead)

        records = self.db.query(Maintenance).filter(
            Maintenance.status == MaintenanceStatus.SCHEDULED,
            Maintenance.next_maintenance_date >= today,
            Maintenance.next_maintenance_date <= future_date
        ).order_by(Maintenance.next_maintenance_date.asc()).all()

        return [
            {
                "id": m.id,
                "car_info": f"{m.car.brand} {m.car.model} ({m.car.license_plate})",
                "maintenance_type": m.maintenance_type.value,
                "next_maintenance_date": m.next_maintenance_date.strftime("%d.%m.%Y"),
                "days_until": (m.next_maintenance_date - today).days
            }
            for m in records
        ]

    def add_maintenance(self, car_id: int, maintenance_type: MaintenanceType,
                        maintenance_date: date, description: str = None,
                        mileage: int = None, next_mileage: int = None,
                        next_maintenance_date: date = None, cost: int = None,
                        performed_by: str = None, notes: str = None) -> Dict[str, Any]:
        """Добавление новой записи ТО."""
        car = self.db.query(Car).filter(Car.id == car_id).first()
        if not car:
            return {"success": False, "error": "Автомобиль не найден"}

        new_maintenance = Maintenance(
            car_id=car_id,
            maintenance_type=maintenance_type,
            maintenance_date=maintenance_date,
            description=description.strip() if description else None,
            mileage=mileage,
            next_mileage=next_mileage,
            next_maintenance_date=next_maintenance_date,
            cost=cost,
            status=MaintenanceStatus.SCHEDULED,
            performed_by=performed_by.strip() if performed_by else None,
            notes=notes.strip() if notes else None
        )

        try:
            self.db.add(new_maintenance)
            self.db.commit()
            self.db.refresh(new_maintenance)

            # Логирование
            from utils.system_utils import log_action
            from models.audit_log import ActionType
            log_action(
                db=self.db,
                action_type=ActionType.CREATE,
                entity_name="Maintenance",
                description=f"Запланировано {maintenance_type.value} для {car.brand} {car.model}",
                entity_id=new_maintenance.id,
                user_info="Admin"
            )

            return {"success": True, "data": new_maintenance}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка БД: {str(e)}"}

    def complete_maintenance(self, maintenance_id: int) -> Dict[str, Any]:
        """Отметить ТО как выполненное."""
        maintenance = self.db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
        if not maintenance:
            return {"success": False, "error": "Запись ТО не найдена"}

        if maintenance.status == MaintenanceStatus.COMPLETED:
            return {"success": False, "error": "ТО уже выполнено"}

        try:
            maintenance.status = MaintenanceStatus.COMPLETED
            self.db.commit()

            from utils.system_utils import log_action
            from models.audit_log import ActionType
            log_action(
                db=self.db,
                action_type=ActionType.UPDATE,
                entity_name="Maintenance",
                description=f"Выполнено {maintenance.maintenance_type.value} для {maintenance.car.brand} {maintenance.car.model}",
                entity_id=maintenance_id,
                user_info="Admin"
            )

            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def cancel_maintenance(self, maintenance_id: int) -> Dict[str, Any]:
        """Отмена ТО."""
        maintenance = self.db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
        if not maintenance:
            return {"success": False, "error": "Запись ТО не найдена"}

        if maintenance.status == MaintenanceStatus.COMPLETED:
            return {"success": False, "error": "Нельзя отменить выполненное ТО"}

        try:
            maintenance.status = MaintenanceStatus.CANCELLED
            self.db.commit()
            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def delete_maintenance(self, maintenance_id: int) -> Dict[str, Any]:
        """Удаление записи ТО."""
        maintenance = self.db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()
        if not maintenance:
            return {"success": False, "error": "Запись ТО не найдена"}

        try:
            self.db.delete(maintenance)
            self.db.commit()
            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def get_statistics(self) -> Dict[str, Any]:
        """Статистика по ТО."""
        total_count = self.db.query(sa_func.count(Maintenance.id)).scalar() or 0
        scheduled_count = self.db.query(sa_func.count(Maintenance.id)).filter(
            Maintenance.status == MaintenanceStatus.SCHEDULED
        ).scalar() or 0
        completed_count = self.db.query(sa_func.count(Maintenance.id)).filter(
            Maintenance.status == MaintenanceStatus.COMPLETED
        ).scalar() or 0
        total_cost = self.db.query(sa_func.sum(Maintenance.cost)).filter(
            Maintenance.status == MaintenanceStatus.COMPLETED
        ).scalar() or 0

        # По типам
        # По типам
        by_type = self.db.query(
            Maintenance.maintenance_type,
            sa_func.count(Maintenance.id).label('count'),
            sa_func.sum(Maintenance.cost).label('total_cost')
        ).group_by(Maintenance.maintenance_type).all()

        return {
            "total_count": total_count,
            "scheduled_count": scheduled_count,
            "completed_count": completed_count,
            "total_cost": total_cost,
            "by_type": [
                {
                    "type": bt[0].value,  # ← ИСПРАВЛЕНО: обращение по индексу
                    "count": bt[1],  # ← ИСПРАВЛЕНО
                    "total_cost": bt[2] or 0  # ← ИСПРАВЛЕНО
                }
                for bt in by_type
            ]
        }

    def add_maintenance(self, car_id: int, maintenance_type: MaintenanceType,
                        maintenance_date: date, description: str = None,
                        mileage: int = None, next_mileage: int = None,
                        next_maintenance_date: date = None, cost: int = None,
                        performed_by: str = None, notes: str = None) -> Dict[str, Any]:
        """Добавление новой записи ТО с проверкой пересечений."""
        car = self.db.query(Car).filter(Car.id == car_id).first()
        if not car:
            return {"success": False, "error": "Автомобиль не найден"}

        # ПРОВЕРКА: пересечение с активными договорами
        from models.agreement import RentalAgreement, AgreementStatus
        from sqlalchemy import and_

        # Определяем период ТО
        m_start = maintenance_date
        m_end = next_maintenance_date if next_maintenance_date else maintenance_date

        overlapping_agreement = self.db.query(RentalAgreement).filter(
            RentalAgreement.car_id == car_id,
            RentalAgreement.status == AgreementStatus.ACTIVE,
            and_(
                RentalAgreement.start_date <= m_end,
                RentalAgreement.end_date >= m_start
            )
        ).first()

        if overlapping_agreement:
            return {
                "success": False,
                "error": f"Автомобиль находится в аренде в этот период (договор №{overlapping_agreement.id}). Завершите договор или перенесите ТО."
            }

        new_maintenance = Maintenance(
            car_id=car_id,
            maintenance_type=maintenance_type,
            maintenance_date=maintenance_date,
            description=description.strip() if description else None,
            mileage=mileage,
            next_mileage=next_mileage,
            next_maintenance_date=next_maintenance_date,
            cost=cost,
            status=MaintenanceStatus.SCHEDULED,
            performed_by=performed_by.strip() if performed_by else None,
            notes=notes.strip() if notes else None
        )

        try:
            self.db.add(new_maintenance)
            self.db.commit()
            self.db.refresh(new_maintenance)

            from utils.system_utils import log_action
            from models.audit_log import ActionType
            log_action(
                db=self.db,
                action_type=ActionType.CREATE,
                entity_name="Maintenance",
                description=f"Запланировано {maintenance_type.value} для {car.brand} {car.model}",
                entity_id=new_maintenance.id,
                user_info="Admin"
            )

            return {"success": True, "data": new_maintenance}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка БД: {str(e)}"}