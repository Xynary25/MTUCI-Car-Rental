from sqlalchemy.orm import Session
from models.penalty import Penalty, PenaltyType, PenaltyStatus
from models.agreement import RentalAgreement
from typing import List, Dict, Any
from datetime import date


class PenaltyController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_penalties(self) -> List[Dict[str, Any]]:
        """Получение списка всех штрафов с информацией о договоре."""
        penalties = (
            self.db.query(Penalty)
            .join(RentalAgreement)
            .order_by(Penalty.date.desc())
            .all()
        )
        result = []
        for p in penalties:
            result.append({
                "id": p.id,
                "agreement_id": p.agreement_id,
                "client_name": p.agreement.client.full_name if p.agreement.client else "Неизвестно",
                "car_info": f"{p.agreement.car.brand} {p.agreement.car.model} ({p.agreement.car.license_plate})" if p.agreement.car else "N/A",
                "penalty_type": p.penalty_type.value,
                "amount": p.amount,
                "description": p.description or "",
                "date": p.date.strftime("%d.%m.%Y"),
                "is_paid": p.is_paid,
                "status": p.status.value
            })
        return result

    def add_penalty(self, agreement_id: int, penalty_type: PenaltyType,
                    amount: int, description: str, penalty_date: date = None) -> Dict[str, Any]:
        """Добавление нового штрафа."""
        if amount <= 0:
            return {"success": False, "error": "Сумма штрафа должна быть больше 0"}

        agreement = self.db.query(RentalAgreement).filter(
            RentalAgreement.id == agreement_id
        ).first()
        if not agreement:
            return {"success": False, "error": "Договор не найден"}

        if penalty_date is None:
            penalty_date = date.today()

        new_penalty = Penalty(
            agreement_id=agreement_id,
            penalty_type=penalty_type,
            amount=amount,
            description=description.strip() if description else None,
            date=penalty_date,
            is_paid=False,
            status=PenaltyStatus.PENDING
        )

        try:
            self.db.add(new_penalty)
            self.db.commit()
            self.db.refresh(new_penalty)
            return {"success": True, "data": new_penalty}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка БД: {str(e)}"}

    def mark_as_paid(self, penalty_id: int) -> Dict[str, Any]:
        """Отметить штраф как оплаченный."""
        penalty = self.db.query(Penalty).filter(Penalty.id == penalty_id).first()
        if not penalty:
            return {"success": False, "error": "Штраф не найден"}

        if penalty.is_paid:
            return {"success": False, "error": "Штраф уже оплачен"}

        try:
            penalty.is_paid = True
            penalty.status = PenaltyStatus.PAID
            self.db.commit()
            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def cancel_penalty(self, penalty_id: int) -> Dict[str, Any]:
        """Отмена штрафа."""
        penalty = self.db.query(Penalty).filter(Penalty.id == penalty_id).first()
        if not penalty:
            return {"success": False, "error": "Штраф не найден"}

        if penalty.is_paid:
            return {"success": False, "error": "Нельзя отменить оплаченный штраф"}

        try:
            penalty.status = PenaltyStatus.CANCELLED
            self.db.commit()
            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def delete_penalty(self, penalty_id: int) -> Dict[str, Any]:
        """Удаление штрафа."""
        penalty = self.db.query(Penalty).filter(Penalty.id == penalty_id).first()
        if not penalty:
            return {"success": False, "error": "Штраф не найден"}

        try:
            self.db.delete(penalty)
            self.db.commit()
            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def get_statistics(self) -> Dict[str, Any]:
        """Статистика по штрафам."""
        from sqlalchemy import func as sa_func

        total_count = self.db.query(sa_func.count(Penalty.id)).scalar() or 0
        total_amount = self.db.query(sa_func.sum(Penalty.amount)).scalar() or 0
        paid_count = self.db.query(sa_func.count(Penalty.id)).filter(
            Penalty.is_paid == True
        ).scalar() or 0
        pending_count = self.db.query(sa_func.count(Penalty.id)).filter(
            Penalty.status == PenaltyStatus.PENDING
        ).scalar() or 0
        paid_amount = self.db.query(sa_func.sum(Penalty.amount)).filter(
            Penalty.is_paid == True
        ).scalar() or 0
        pending_amount = self.db.query(sa_func.sum(Penalty.amount)).filter(
            Penalty.status == PenaltyStatus.PENDING
        ).scalar() or 0

        return {
            "total_count": total_count,
            "total_amount": total_amount,
            "paid_count": paid_count,
            "pending_count": pending_count,
            "paid_amount": paid_amount,
            "pending_amount": pending_amount,
            "by_type": []
        }