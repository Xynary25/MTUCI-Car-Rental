import csv
from datetime import date
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox, QGroupBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from sqlalchemy import func
from database import SessionLocal
from controllers.report_controller import ReportController
from models.car import Car
from models.agreement import RentalAgreement, AgreementStatus
from models.payment import Payment, PaymentStatus
from models.expense import Expense


class ReportWidget(QWidget):
    """Виджет раздела «Отчёты и экспорт данных»."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.controller = ReportController(self.db)
        self.current_user = current_user  # Получаем пользователя из параметра

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок раздела
        header_label = QLabel("📑 Отчёты и экспорт данных")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # ПРОВЕРКА ПРАВ: просмотр отчётов
        if self.current_user and not self.current_user.has_permission('view_reports'):
            no_access_label = QLabel(
                "⛔ У вас нет прав для просмотра отчётов.\n"
                "Обратитесь к администратору системы."
            )
            no_access_label.setObjectName("no_access_label")
            no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_access_label.setStyleSheet("font-size: 16px; color: #64748B; padding: 40px;")
            layout.addWidget(no_access_label)
            layout.addStretch()
            return

        # ===== Группа: Экспорт договоров аренды =====
        # Показываем только при наличии права export_reports
        if self.current_user and self.current_user.has_permission('export_reports'):
            export_group = QGroupBox("📄 Экспорт договоров аренды")
            export_layout = QVBoxLayout(export_group)

            self.export_label = QLabel(
                "Выгрузите реестр заключённых договоров аренды в формат CSV "
                "для дальнейшей обработки в MS Excel или передачи в бухгалтерию. "
                "Файл сохраняется в кодировке UTF-8 с BOM для корректного "
                "отображения кириллицы."
            )
            self.export_label.setWordWrap(True)
            export_layout.addWidget(self.export_label)

            self.export_btn = QPushButton("📥 Экспортировать реестр договоров в CSV")
            self.export_btn.setMinimumHeight(45)
            self.export_btn.clicked.connect(self.export_data)
            export_layout.addWidget(self.export_btn)

            layout.addWidget(export_group)

            # ===== Группа: Экспорт финансовой статистики =====
            stats_group = QGroupBox("📊 Экспорт финансовой статистики")
            stats_layout = QVBoxLayout(stats_group)

            self.stats_label = QLabel(
                "Сформируйте сводный отчёт по доходам, расходам и чистой прибыли "
                "за выбранный период. Отчёт включает:\n"
                "• Общие доходы от аренды\n"
                "• Общие расходы (ремонты, страховки, прочее)\n"
                "• Чистую прибыль\n"
                "• Топ-10 автомобилей по доходности\n"
                "• Статистику по статусам договоров"
            )
            self.stats_label.setWordWrap(True)
            stats_layout.addWidget(self.stats_label)

            # Период отчёта
            period_layout = QHBoxLayout()
            period_layout.addWidget(QLabel("Период с:"))
            self.date_from = QDateEdit()
            self.date_from.setCalendarPopup(True)
            self.date_from.setDate(QDate.currentDate().addMonths(-1))
            self.date_from.setMinimumHeight(40)
            period_layout.addWidget(self.date_from)

            period_layout.addWidget(QLabel("по:"))
            self.date_to = QDateEdit()
            self.date_to.setCalendarPopup(True)
            self.date_to.setDate(QDate.currentDate())
            self.date_to.setMinimumHeight(40)
            period_layout.addWidget(self.date_to)

            period_layout.addStretch()
            stats_layout.addLayout(period_layout)

            self.stats_btn = QPushButton("📥 Экспортировать статистику в CSV")
            self.stats_btn.setMinimumHeight(45)
            self.stats_btn.clicked.connect(self.export_stats)
            stats_layout.addWidget(self.stats_btn)

            layout.addWidget(stats_group)
        else:
            # Если нет прав на экспорт — показываем информационное сообщение
            info_label = QLabel(
                "ℹ️ У вас есть право на просмотр отчётов, но нет права на их экспорт.\n"
                "Для выгрузки данных в CSV обратитесь к администратору."
            )
            info_label.setObjectName("hint_label")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_label.setWordWrap(True)
            info_label.setStyleSheet("font-size: 14px; color: #64748B; padding: 30px;")
            layout.addWidget(info_label)

        layout.addStretch()

    def export_data(self):
        """Экспорт реестра договоров."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('export_reports'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для экспорта отчётов")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить отчёт",
            "agreements_report.csv",
            "CSV Files (*.csv)"
        )
        if filepath:
            result = self.controller.export_agreements_to_csv(filepath)
            if result["success"]:
                QMessageBox.information(
                    self, "Успех", f"Отчёт успешно сохранён:\n{filepath}"
                )
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def export_stats(self):
        """Полноценный экспорт финансовой статистики в CSV."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('export_reports'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для экспорта отчётов")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить статистику",
            "statistics_report.csv",
            "CSV Files (*.csv)"
        )
        if not filepath:
            return

        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        try:
            # 1. Доходы от платежей за период
            total_income = self.db.query(func.sum(Payment.amount)).filter(
                Payment.status == PaymentStatus.PAID,
                Payment.payment_date >= date_from,
                Payment.payment_date <= date_to
            ).scalar() or 0

            # 2. Расходы за период
            total_expenses = self.db.query(func.sum(Expense.amount)).filter(
                Expense.date >= date_from,
                Expense.date <= date_to
            ).scalar() or 0

            # 3. Чистая прибыль
            net_profit = total_income - total_expenses

            # 4. Статистика по договорам
            total_agreements = self.db.query(func.count(RentalAgreement.id)).filter(
                RentalAgreement.start_date >= date_from,
                RentalAgreement.end_date <= date_to
            ).scalar() or 0

            active_agreements = self.db.query(func.count(RentalAgreement.id)).filter(
                RentalAgreement.status == AgreementStatus.ACTIVE,
                RentalAgreement.start_date >= date_from,
                RentalAgreement.end_date <= date_to
            ).scalar() or 0

            completed_agreements = self.db.query(func.count(RentalAgreement.id)).filter(
                RentalAgreement.status == AgreementStatus.COMPLETED,
                RentalAgreement.start_date >= date_from,
                RentalAgreement.end_date <= date_to
            ).scalar() or 0

            # 5. Топ-10 автомобилей по доходности
            top_cars = self.db.query(
                Car.brand, Car.model, Car.license_plate,
                func.count(RentalAgreement.id).label('rentals_count'),
                func.sum(RentalAgreement.total_cost).label('total_revenue')
            ).join(RentalAgreement).filter(
                RentalAgreement.start_date >= date_from,
                RentalAgreement.end_date <= date_to
            ).group_by(Car.id).order_by(
                func.sum(RentalAgreement.total_cost).desc()
            ).limit(10).all()

            # 6. Расходы по типам
            expenses_by_type = self.db.query(
                Expense.expense_type,
                func.count(Expense.id).label('count'),
                func.sum(Expense.amount).label('total')
            ).filter(
                Expense.date >= date_from,
                Expense.date <= date_to
            ).group_by(Expense.expense_type).all()

            # Запись в CSV
            with open(filepath, mode='w', encoding='utf-8-sig', newline='') as file:
                writer = csv.writer(file, delimiter=';')

                # Шапка отчёта
                writer.writerow(["ОТЧЁТ ПО ФИНАНСОВОЙ СТАТИСТИКЕ"])
                writer.writerow([f"Период: с {date_from.strftime('%d.%m.%Y')} по {date_to.strftime('%d.%m.%Y')}"])
                writer.writerow([f"Дата формирования: {date.today().strftime('%d.%m.%Y')}"])
                writer.writerow([])

                # Финансовые показатели
                writer.writerow(["ФИНАНСОВЫЕ ПОКАЗАТЕЛИ"])
                writer.writerow(["Показатель", "Сумма (руб.)"])
                writer.writerow(["Общие доходы от аренды", total_income])
                writer.writerow(["Общие расходы", total_expenses])
                writer.writerow(["Чистая прибыль", net_profit])
                writer.writerow([])

                # Статистика по договорам
                writer.writerow(["СТАТИСТИКА ПО ДОГОВОРАМ"])
                writer.writerow(["Показатель", "Количество"])
                writer.writerow(["Всего договоров за период", total_agreements])
                writer.writerow(["Активных договоров", active_agreements])
                writer.writerow(["Завершённых договоров", completed_agreements])
                writer.writerow([])

                # Топ автомобилей
                writer.writerow(["ТОП-10 АВТОМОБИЛЕЙ ПО ДОХОДНОСТИ"])
                writer.writerow(["#", "Автомобиль", "Гос. номер", "Кол-во аренд", "Общий доход (руб.)"])
                for i, car in enumerate(top_cars, 1):
                    writer.writerow([
                        i,
                        f"{car.brand} {car.model}",
                        car.license_plate,
                        car.rentals_count,
                        car.total_revenue or 0
                    ])
                writer.writerow([])

                # Расходы по типам
                writer.writerow(["РАСХОДЫ ПО ТИПАМ"])
                writer.writerow(["Тип расхода", "Кол-во операций", "Сумма (руб.)"])
                for exp in expenses_by_type:
                    writer.writerow([
                        exp.expense_type.value,
                        exp.count,
                        exp.total or 0
                    ])

            QMessageBox.information(
                self, "Успех",
                f"Статистика успешно экспортирована:\n{filepath}\n\n"
                f"Доходы: {total_income} руб.\n"
                f"Расходы: {total_expenses} руб.\n"
                f"Прибыль: {net_profit} руб."
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сформировать отчёт:\n{str(e)}"
            )

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)