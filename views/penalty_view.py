from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QDialog, QFormLayout, QComboBox, QSpinBox, QLineEdit,
                             QMessageBox, QHeaderView, QAbstractItemView, QLabel, QDateEdit,
                             QGroupBox, QFrame)
from PyQt6.QtCore import Qt, QDate
from database import SessionLocal
from controllers.penalty_controller import PenaltyController
from models.penalty import PenaltyType, PenaltyStatus
from models.agreement import RentalAgreement, AgreementStatus


class PenaltyDialog(QDialog):
    """Диалог добавления нового штрафа."""

    def __init__(self, parent=None, agreement_id: int = None):
        super().__init__(parent)
        self.setWindowTitle("Добавить штраф / повреждение")
        self.resize(450, 350)
        self.db = SessionLocal()
        self.selected_agreement_id = agreement_id

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Выбор договора
        self.agreement_combo = QComboBox()
        self.agreement_combo.setMinimumHeight(40)
        active_agreements = self.db.query(RentalAgreement).filter(
            RentalAgreement.status == AgreementStatus.ACTIVE
        ).all()
        for a in active_agreements:
            client_name = a.client.full_name if a.client else "Неизвестно"
            car_info = f"{a.car.brand} {a.car.model} ({a.car.license_plate})" if a.car else "N/A"
            self.agreement_combo.addItem(
                f"Договор №{a.id}: {client_name} - {car_info}",
                a.id
            )
        if agreement_id:
            for i in range(self.agreement_combo.count()):
                if self.agreement_combo.itemData(i) == agreement_id:
                    self.agreement_combo.setCurrentIndex(i)
                    break

        # Тип штрафа
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(40)
        for pt in PenaltyType:
            self.type_combo.addItem(pt.value, pt)

        # Сумма
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(100, 1000000)
        self.amount_spin.setValue(1000)
        self.amount_spin.setSuffix(" руб.")
        self.amount_spin.setMinimumHeight(40)

        # Описание
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Подробное описание нарушения/повреждения")
        self.desc_input.setMinimumHeight(40)

        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(40)

        layout.addRow("📋 Договор:", self.agreement_combo)
        layout.addRow("⚠️ Тип:", self.type_combo)
        layout.addRow("💰 Сумма:", self.amount_spin)
        layout.addRow(" Описание:", self.desc_input)
        layout.addRow("📅 Дата:", self.date_edit)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton(" Отмена")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)

    def get_data(self) -> dict:
        return {
            "agreement_id": self.agreement_combo.currentData(),
            "penalty_type": self.type_combo.currentData(),
            "amount": self.amount_spin.value(),
            "description": self.desc_input.text(),
            "date": self.date_edit.date().toPyDate()
        }

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


class PenaltyWidget(QWidget):
    """Виджет раздела «Штрафы и повреждения»."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.controller = PenaltyController(self.db)
        self.all_penalties = []
        self.current_user = current_user  # Получаем пользователя из параметра

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        header_label = QLabel("⚠️ Штрафы и повреждения")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # Карточки со статистикой
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.total_card = self._create_stat_card("Всего штрафов", "0", "#64748B")
        self.pending_card = self._create_stat_card("Не оплачено", "0 руб.", "#EF4444")
        self.paid_card = self._create_stat_card("Оплачено", "0 руб.", "#10B981")

        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.pending_card)
        stats_layout.addWidget(self.paid_card)
        layout.addLayout(stats_layout)

        # Панель инструментов — кнопки создаются ВСЕГДА, проверка прав при клике
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить штраф")
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_penalty)

        self.pay_btn = QPushButton("✅ Отметить оплаченным")
        self.pay_btn.setMinimumHeight(45)
        self.pay_btn.clicked.connect(self.mark_paid)

        self.cancel_btn = QPushButton("❌ Отменить штраф")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.cancel_penalty)

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.setMinimumHeight(45)
        self.delete_btn.clicked.connect(self.delete_penalty)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_data)

        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.pay_btn)
        toolbar.addWidget(self.cancel_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_btn)
        layout.addLayout(toolbar)

        # Таблица
        self.table = QTableWidget()
        self.table.setObjectName("penalty_table")
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Договор", "Клиент", "Автомобиль", "Тип", "Сумма (руб.)", "Дата", "Статус"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(350)
        layout.addWidget(self.table)

        self.load_data()

    def _create_stat_card(self, title: str, value: str, color: str) -> QFrame:
        """Создание карточки статистики."""
        card = QFrame()
        card.setObjectName("dashboard_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("card_title")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_value = QLabel(value)
        lbl_value.setObjectName("card_value")
        lbl_value.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value)
        return card

    def load_data(self):
        """Загрузка данных о штрафах."""
        self.all_penalties = self.controller.get_all_penalties()
        self.display_penalties(self.all_penalties)
        self.update_stats()

    def display_penalties(self, penalties):
        """Отображение штрафов в таблице."""
        self.table.setRowCount(len(penalties))
        for row, p in enumerate(penalties):
            self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(f"№{p['agreement_id']}"))
            self.table.setItem(row, 2, QTableWidgetItem(p["client_name"]))
            self.table.setItem(row, 3, QTableWidgetItem(p["car_info"]))
            self.table.setItem(row, 4, QTableWidgetItem(p["penalty_type"]))
            self.table.setItem(row, 5, QTableWidgetItem(str(p["amount"])))
            self.table.setItem(row, 6, QTableWidgetItem(p["date"]))

            status_item = QTableWidgetItem(p["status"])
            if p["status"] == "Оплачен":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif p["status"] == "Не оплачен":
                status_item.setForeground(Qt.GlobalColor.red)
            elif p["status"] == "Отменён":
                status_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 7, status_item)
        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.table, min_height=40)

    def update_stats(self):
        """Обновление карточек статистики."""
        stats = self.controller.get_statistics()

        for card, key, suffix in [
            (self.total_card, "total_count", " шт."),
            (self.pending_card, "pending_amount", " руб."),
            (self.paid_card, "paid_amount", " руб.")
        ]:
            labels = card.findChildren(QLabel)
            if len(labels) >= 2:
                value = stats.get(key, 0)
                labels[1].setText(f"{value}{suffix}")

    def add_penalty(self):
        """Добавление нового штрафа."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('create_penalty'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для добавления штрафов")
            return

        dialog = PenaltyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            result = self.controller.add_penalty(
                agreement_id=data["agreement_id"],
                penalty_type=data["penalty_type"],
                amount=data["amount"],
                description=data["description"],
                penalty_date=data["date"]
            )
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "Штраф успешно добавлен.")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def mark_paid(self):
        """Отметить штраф как оплаченный."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('edit_penalty'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для изменения статусов штрафов")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите штраф")
            return
        row = selected[0].row()
        penalty_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 7).text()

        if status == "Оплачен":
            QMessageBox.warning(self, "Внимание", "Штраф уже оплачен")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Отметить штраф №{penalty_id} как оплаченный?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.mark_as_paid(penalty_id)
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "Штраф отмечен как оплаченный")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def cancel_penalty(self):
        """Отмена штрафа."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('edit_penalty'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для отмены штрафов")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите штраф")
            return
        row = selected[0].row()
        penalty_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 7).text()

        if status == "Оплачен":
            QMessageBox.warning(self, "Внимание", "Нельзя отменить оплаченный штраф")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Отменить штраф №{penalty_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.cancel_penalty(penalty_id)
            if result["success"]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def delete_penalty(self):
        """Удаление штрафа."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('delete_penalty'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для удаления штрафов")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите штраф")
            return
        row = selected[0].row()
        penalty_id = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить штраф №{penalty_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.delete_penalty(penalty_id)
            if result["success"]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)