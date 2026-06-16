import csv
from sqlalchemy.orm import Session
from models.agreement import RentalAgreement
from models.client import Client
from models.car import Car
from utils.system_utils import log_action, ActionType


class ReportController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def export_agreements_to_csv(self, filepath: str) -> dict:
        """Экспорт всех договоров аренды в формат CSV."""
        try:
            # Запрос с объединением таблиц для получения читаемых данных
            query = self.db.query(
                RentalAgreement.id,
                Client.full_name,
                Car.brand,
                Car.model,
                Car.license_plate,
                RentalAgreement.start_date,
                RentalAgreement.end_date,
                RentalAgreement.total_cost,
                RentalAgreement.status
            ).join(Client).join(Car).all()

            with open(filepath, mode='w', encoding='utf-8-sig', newline='') as file:
                # utf-8-sig обеспечивает корректное открытие кириллицы в MS Excel
                writer = csv.writer(file, delimiter=';')

                # Заголовки столбцов
                writer.writerow([
                    "ID Договора", "Клиент", "Марка", "Модель", "Гос. номер",
                    "Дата начала", "Дата окончания", "Стоимость (руб.)", "Статус"
                ])

                # Данные
                for row in query:
                    writer.writerow([
                        row.id,
                        row.full_name,
                        row.brand,
                        row.model,
                        row.license_plate,
                        row.start_date.strftime("%d.%m.%Y"),
                        row.end_date.strftime("%d.%m.%Y"),
                        row.total_cost,
                        row.status.value
                    ])

            # Логирование успешного экспорта
            log_action(
                db=self.db,
                action_type=ActionType.EXPORT,
                entity_name="Agreement",
                description=f"Экспорт отчёта в файл: {filepath}",
                user_info="Admin"
            )

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Ошибка при создании отчёта: {str(e)}"}