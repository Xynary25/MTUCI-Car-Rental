from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt, QTimer
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
        self.current_user = current_user

        # Создаем UI
        self.init_ui()

        # Загружаем данные
        self.refresh_data()

        # Таймер автообновления каждые 30 секунд
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # 30 секунд

    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📊 Панель управления")
        title.setObjectName("dashboard_title")
        layout.addWidget(title)

        # Индикатор автообновления
        self.auto_refresh_label = QLabel("🔄 Автообновление каждые 30 секунд")
        self.auto_refresh_label.setStyleSheet("font-size: 12px; color: #64748B; font-style: italic;")
        layout.addWidget(self.auto_refresh_label)

        # Сетка карточек
        self.grid = QGridLayout()
        self.grid.setSpacing(20)

        # Создаем карточки (пока пустые)
        self.card_cars = self.create_card(" Всего автомобилей", "—")
        self.card_agreements = self.create_card(" Активных договоров", "—")
        self.card_clients = self.create_card("👥 Всего клиентов", "—")
        self.card_revenue = self.create_card("💰 Выручка за месяц", "— руб.")

        self.grid.addWidget(self.card_cars, 0, 0)
        self.grid.addWidget(self.card_agreements, 0, 1)
        self.grid.addWidget(self.card_clients, 1, 0)
        self.grid.addWidget(self.card_revenue, 1, 1)

        layout.addLayout(self.grid)
        layout.addStretch()

    def refresh_data(self):
        """Обновление данных дашборда."""
        try:
            # Пересоздаем сессию для получения свежих данных
            self.db.close()
            self.db = SessionLocal()

            # Запрашиваем данные
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

            self.update_card(self.card_cars, "🚗 Всего автомобилей", str(total_cars))
            self.update_card(self.card_agreements, "📝 Активных договоров", str(active_agreements))
            self.update_card(self.card_clients, " Всего клиентов", str(total_clients))
            self.update_card(self.card_revenue, "💰 Выручка за месяц", f"{revenue} руб.")

            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.auto_refresh_label.setText(f"🔄 Обновлено: {current_time} (автообновление каждые 30 сек)")

        except Exception as e:
            print(f"Ошибка обновления дашборда: {e}")

    def update_card(self, card, title, value):
        """Обновление содержимого карточки."""
        # Находим виджеты внутри карточки
        for i in range(card.layout().count()):
            widget = card.layout().itemAt(i).widget()
            if isinstance(widget, QLabel):
                if widget.objectName() == "card_title":
                    widget.setText(title)
                elif widget.objectName() == "card_value":
                    widget.setText(value)

    def create_card(self, title, value):
        """Создание информационной карточки."""
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
        """Остановка таймера при закрытии."""
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        self.db.close()
        super().closeEvent(event)