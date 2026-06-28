from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.client import Client
from typing import List, Dict, Any
from utils.system_utils import log_action
from models.audit_log import ActionType
import re


class ClientController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_clients(self) -> List[Dict[str, Any]]:
        clients = self.db.query(Client).all()
        return [
            {
                "id": c.id,
                "full_name": c.full_name,
                "passport": f"{c.passport_series} {c.passport_number}",
                "phone": c.phone,
                "email": c.email or "Не указан"
            }
            for c in clients
        ]

    def add_client(self, full_name: str, passport_series: str, passport_number: str,
                   phone: str, email: str) -> Dict[str, Any]:
        # Валидация
        if not re.match(r"^\d{4}$", passport_series):
            return {"success": False, "error": "Серия паспорта должна состоять из 4 цифр."}
        if not re.match(r"^\d{6}$", passport_number):
            return {"success": False, "error": "Номер паспорта должен состоять из 6 цифр."}
        if not re.match(r"^\+7\d{10}$", phone.replace(" ", "").replace("-", "")):
            return {"success": False, "error": "Неверный формат телефона. Используйте формат +7XXXXXXXXXX."}

        new_client = Client(
            full_name=full_name.strip(),
            passport_series=passport_series.strip(),
            passport_number=passport_number.strip(),
            phone=phone.strip(),
            email=email.strip() if email else None
        )
        try:
            self.db.add(new_client)
            self.db.commit()
            self.db.refresh(new_client)

            log_action(
                db=self.db,
                action_type=ActionType.CREATE,
                entity_name="Client",
                description=f"Добавлен клиент: {new_client.full_name} ({new_client.phone})",
                entity_id=new_client.id,
                user_info="Admin"
            )

            return {"success": True, "data": new_client}
        except IntegrityError:
            self.db.rollback()
            return {"success": False, "error": "Клиент с таким номером телефона или email уже существует."}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка БД: {str(e)}"}

    def delete_client(self, client_id: int) -> Dict[str, Any]:
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"success": False, "error": "Клиент не найден."}

        if client.agreements:
            return {"success": False, "error": "Невозможно удалить клиента, у которого есть история договоров."}

        client_name = client.full_name

        try:
            self.db.delete(client)
            self.db.commit()

            log_action(
                db=self.db,
                action_type=ActionType.DELETE,
                entity_name="Client",
                description=f"Удалён клиент: {client_name}",
                entity_id=client_id,
                user_info="Admin"
            )

            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка при удалении: {str(e)}"}