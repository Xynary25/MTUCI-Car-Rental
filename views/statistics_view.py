from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox,
                             QMessageBox, QHeaderView, QAbstractItemView, QLabel, QDateEdit,
                             QGroupBox, QFrame)
from PyQt6.QtCore import Qt, QDate
from sqlalchemy import func
from database import SessionLocal
from models.car import Car
from models.agreement import RentalAgreement
from models.expense import Expense, ExpenseType


class ExpenseDialog(QDialog):
    """Диалог добавления расхода/ремонта."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить расход / ремонт")
        self.resize(400, 300)
        self.db = SessionLocal()

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.car_combo = QComboBox()
        self.car_combo.setMinimumHeight(40)
        self.car_combo.addItem("Не привязано к авто", None)
        for c in self.db.query(Car).all():
            self.car_combo.addItem(f"{c.brand} {c.model} ({c.license_plate})", c.id)

        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(40)
        for t in ExpenseType:
            self.type_combo.addItem(t.value, t)

        self.amount_input = QSpinBox()
        self.amount_input.setRange(1, 10000000)
        self.amount_input.setSuffix(" руб.")
        self.amount_input.setMinimumHeight(40)

        self.desc_input = QLineEdit()
        self.desc_input.setMinimumHeight(40)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(40)

        layout.addRow("🚗 Автомобиль:", self.car_combo)
        layout.addRow("🔧 Тип расхода:", self.type_combo)
        layout.addRow("💰 Сумма:", self.amount_input)
        layout.addRow("📄 Описание:", self.desc_input)
        layout.addRow("📅 Дата:", self.date_edit)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            "car_id": self.car_combo.currentData(),
            "expense_type": self.type_combo.currentData(),
            "amount": self.amount_input.value(),
            "description": self.desc_input.text(),
            "date": self.date_edit.date().toPyDate()
        }

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


class StatisticsWidget(QWidget):
    """Виджет раздела «Аналитика и Статистика»."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.current_user = current_user  # Получаем пользователя из параметра

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Проверка прав
        if self.current_user and not self.current_user.has_permission('view_statistics'):
            no_access_label = QLabel(
                "⛔ У вас нет прав для просмотра статистики.\n"
                "Обратитесь к администратору системы."
            )
            no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_access_label.setStyleSheet("font-size: 16px; color: #64748B; padding: 40px;")
            layout.addWidget(no_access_label)
            layout.addStretch()
            return

        # Заголовок раздела — через objectName, стили из theme_manager
        title = QLabel("📈 Аналитика и Статистика")
        title.setObjectName("section_header")
        layout.addWidget(title)

        # ===== Группа: Учет расходов и ремонтов =====
        expense_group = QGroupBox("🔧 Учет расходов и ремонтов")
        expense_layout = QVBoxLayout(expense_group)

        self.expense_table = QTableWidget()
        self.expense_table.setObjectName("expense_table")
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels([
            "Дата", "Авто", "Тип", "Описание", "Сумма (руб.)"
        ])
        self.expense_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.expense_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.expense_table.setAlternatingRowColors(True)
        self.expense_table.setMinimumHeight(250)
        expense_layout.addWidget(self.expense_table)

        btn_layout = QHBoxLayout()

        if self.current_user and self.current_user.has_permission('create_expense'):
            self.add_expense_btn = QPushButton("➕ Добавить расход")
            self.add_expense_btn.setMinimumHeight(45)
            self.add_expense_btn.clicked.connect(self.add_expense)
            btn_layout.addWidget(self.add_expense_btn)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_data)

        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        expense_layout.addLayout(btn_layout)
        layout.addWidget(expense_group)

        # ===== Группа: Топ популярных автомобилей =====
        top_group = QGroupBox("🏆 Топ популярных автомобилей (по кол-ву договоров)")
        top_layout = QVBoxLayout(top_group)

        self.top_table = QTableWidget()
        self.top_table.setObjectName("top_table")
        self.top_table.setColumnCount(3)
        self.top_table.setHorizontalHeaderLabels([
            "Автомобиль", "Кол-во аренд", "Общий доход (руб.)"
        ])
        self.top_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.top_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.top_table.setAlternatingRowColors(True)
        self.top_table.setMinimumHeight(200)
        top_layout.addWidget(self.top_table)
        layout.addWidget(top_group)

        self.load_data()

    def load_data(self):
        """Загрузка данных в таблицы."""
        # Таблица расходов
        expenses = self.db.query(Expense).order_by(Expense.date.desc()).all()
        self.expense_table.setRowCount(len(expenses))
        for row, exp in enumerate(expenses):
            car_info = f"{exp.car.brand} {exp.car.model}" if exp.car else "Не привязано"
            self.expense_table.setItem(row, 0, QTableWidgetItem(exp.date.strftime("%d.%m.%Y")))
            self.expense_table.setItem(row, 1, QTableWidgetItem(car_info))
            self.expense_table.setItem(row, 2, QTableWidgetItem(exp.expense_type.value))
            self.expense_table.setItem(row, 3, QTableWidgetItem(exp.description or " "))
            self.expense_table.setItem(row, 4, QTableWidgetItem(str(exp.amount)))

        # Таблица топа автомобилей: сортировка по количеству аренд (убывание), затем по доходу (убывание)
        top_cars = (
            self.db.query(
                Car.brand, Car.model, Car.license_plate,
                func.count(RentalAgreement.id).label('count'),
                func.sum(RentalAgreement.total_cost).label('revenue')
            )
            .join(RentalAgreement)
            .group_by(Car.id)
            .order_by(
                func.count(RentalAgreement.id).desc(),  # Сначала по количеству аренд
                func.sum(RentalAgreement.total_cost).desc()  # Затем по доходу
            )
            .limit(5)
            .all()
        )

        self.top_table.setRowCount(len(top_cars))
        for row, car in enumerate(top_cars):
            self.top_table.setItem(row, 0, QTableWidgetItem(
                f"{car.brand} {car.model} ({car.license_plate})"
            ))
            self.top_table.setItem(row, 1, QTableWidgetItem(str(car.count)))
            self.top_table.setItem(row, 2, QTableWidgetItem(str(car.revenue or 0)))

        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.expense_table, min_height=40)
        auto_resize_table_rows(self.top_table, min_height=40)

    def add_expense(self):
        """Добавление нового расхода."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('create_expense'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для добавления расходов")
            return

        dialog = ExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.get_data()
                expense = Expense(
                    car_id=data["car_id"],
                    expense_type=data["expense_type"],
                    amount=data["amount"],
                    description=data["description"],
                    date=data["date"]
                )
                self.db.add(expense)
                self.db.commit()

                from utils.system_utils import log_action
                from models.audit_log import ActionType

                car_info = f" (авто: {expense.car.brand} {expense.car.model})" if expense.car else ""
                log_action(
                    db=self.db,
                    action_type=ActionType.CREATE,
                    entity_name="Expense",
                    description=f"Добавлен расход: {expense.expense_type.value} на сумму {expense.amount} руб.{car_info}",
                    entity_id=expense.id,
                    user_info="Admin"
                )

                self.load_data()
                QMessageBox.information(self, "Успех", "Расход успешно добавлен.")
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить расход:\n{str(e)}")

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)