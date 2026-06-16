from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from sqlalchemy import func
from database import SessionLocal
from models.car import Car
from models.client import Client
from models.agreement import RentalAgreement, AgreementStatus
from models.payment import Payment, PaymentStatus
from datetime import date


class DashboardWidget(QWidget):
    """Виджет главной панели управления (Дашборд)."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.current_user = current_user  # Получаем текущего пользователя

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📊 Панель управления")
        title.setObjectName("dashboard_title")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(20)

        total_cars = self.db.query(func.count(Car.id)).scalar() or 0
        active_agreements = self.db.query(func.count(RentalAgreement.id)).filter(
            RentalAgreement.status == AgreementStatus.ACTIVE
        ).scalar() or 0
        total_clients = self.db.query(func.count(Client.id)).scalar() or 0

        first_day_of_month = date.today().replace(day=1)
        revenue = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.PAID,
            Payment.payment_date >= first_day_of_month
        ).scalar() or 0

        grid.addWidget(self.create_card("🚗 Всего автомобилей", str(total_cars)), 0, 0)
        grid.addWidget(self.create_card("📝 Активных договоров", str(active_agreements)), 0, 1)
        grid.addWidget(self.create_card("👥 Всего клиентов", str(total_clients)), 1, 0)
        grid.addWidget(self.create_card("💰 Выручка за месяц", f"{revenue} руб."), 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

    def create_card(self, title, value):
        """Создание информационной карточки (стили через QSS)."""
        card = QFrame()
        card.setObjectName("dashboard_card")

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("card_title")

        lbl_value = QLabel(value)
        lbl_value.setObjectName("card_value")

        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value)
        return card

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)