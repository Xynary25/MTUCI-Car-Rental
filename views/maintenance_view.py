from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QDialog, QFormLayout, QComboBox, QSpinBox, QLineEdit,
                             QMessageBox, QHeaderView, QAbstractItemView, QLabel, QDateEdit,
                             QGroupBox, QFrame)
from PyQt6.QtCore import Qt, QDate
from database import SessionLocal
from controllers.maintenance_controller import MaintenanceController
from models.maintenance import MaintenanceType, MaintenanceStatus
from models.car import Car


class MaintenanceDialog(QDialog):
    """Диалог добавления записи ТО."""

    def __init__(self, parent=None, car_id: int = None):
        super().__init__(parent)
        self.setWindowTitle("Добавить техническое обслуживание")
        self.resize(500, 450)
        self.db = SessionLocal()

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Выбор автомобиля
        self.car_combo = QComboBox()
        self.car_combo.setMinimumHeight(40)
        for c in self.db.query(Car).all():
            self.car_combo.addItem(f"{c.brand} {c.model} ({c.license_plate})", c.id)
        if car_id:
            for i in range(self.car_combo.count()):
                if self.car_combo.itemData(i) == car_id:
                    self.car_combo.setCurrentIndex(i)
                    break

        # Тип ТО
        self.type_combo = QComboBox()
        self.type_combo.setMinimumHeight(40)
        for mt in MaintenanceType:
            self.type_combo.addItem(mt.value, mt)

        # Дата ТО
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setMinimumHeight(40)

        # Пробег
        self.mileage_spin = QSpinBox()
        self.mileage_spin.setRange(0, 1000000)
        self.mileage_spin.setSuffix(" км")
        self.mileage_spin.setMinimumHeight(40)

        # Следующее ТО (дата)
        self.next_date_edit = QDateEdit()
        self.next_date_edit.setCalendarPopup(True)
        self.next_date_edit.setDate(QDate.currentDate().addMonths(6))
        self.next_date_edit.setMinimumHeight(40)

        # Следующее ТО (пробег)
        self.next_mileage_spin = QSpinBox()
        self.next_mileage_spin.setRange(0, 1000000)
        self.next_mileage_spin.setSuffix(" км")
        self.next_mileage_spin.setMinimumHeight(40)

        # Стоимость
        self.cost_spin = QSpinBox()
        self.cost_spin.setRange(0, 1000000)
        self.cost_spin.setSuffix(" руб.")
        self.cost_spin.setMinimumHeight(40)

        # Описание
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Описание работ")
        self.desc_input.setMinimumHeight(40)

        # Кто выполнял
        self.performed_by_input = QLineEdit()
        self.performed_by_input.setPlaceholderText("Название СТО или мастер")
        self.performed_by_input.setMinimumHeight(40)

        layout.addRow("🚗 Автомобиль:", self.car_combo)
        layout.addRow("🔧 Тип ТО:", self.type_combo)
        layout.addRow("📅 Дата ТО:", self.date_edit)
        layout.addRow("🛣️ Пробег:", self.mileage_spin)
        layout.addRow("📅 Следующее ТО:", self.next_date_edit)
        layout.addRow("🛣️ Следующий пробег:", self.next_mileage_spin)
        layout.addRow("💰 Стоимость:", self.cost_spin)
        layout.addRow("📄 Описание:", self.desc_input)
        layout.addRow("👤 Кто выполнял:", self.performed_by_input)

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

    def get_data(self) -> dict:
        return {
            "car_id": self.car_combo.currentData(),
            "maintenance_type": self.type_combo.currentData(),
            "maintenance_date": self.date_edit.date().toPyDate(),
            "mileage": self.mileage_spin.value() if self.mileage_spin.value() > 0 else None,
            "next_maintenance_date": self.next_date_edit.date().toPyDate(),
            "next_mileage": self.next_mileage_spin.value() if self.next_mileage_spin.value() > 0 else None,
            "cost": self.cost_spin.value() if self.cost_spin.value() > 0 else None,
            "description": self.desc_input.text(),
            "performed_by": self.performed_by_input.text()
        }

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


class MaintenanceWidget(QWidget):
    """Виджет раздела «Техническое обслуживание»."""

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user  # Получаем текущего пользователя
        self.db = SessionLocal()
        self.controller = MaintenanceController(self.db)
        self.all_maintenance = []

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        header_label = QLabel("🔧 Техническое обслуживание")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # ПРОВЕРКА ПРАВ: просмотр ТО
        if self.current_user and not self.current_user.has_permission('view_maintenance'):
            no_access_label = QLabel(
                "⛔ У вас нет прав для просмотра раздела ТО.\n"
                "Обратитесь к администратору системы."
            )
            no_access_label.setObjectName("no_access_label")
            no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_access_label.setStyleSheet("font-size: 16px; color: #64748B; padding: 40px;")
            layout.addWidget(no_access_label)
            layout.addStretch()
            return

        # Карточки со статистикой
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)

        self.total_card = self._create_stat_card("Всего записей", "0", "#64748B")
        self.scheduled_card = self._create_stat_card("Запланировано", "0", "#F59E0B")
        self.completed_card = self._create_stat_card("Выполнено", "0 руб.", "#10B981")

        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.scheduled_card)
        stats_layout.addWidget(self.completed_card)
        layout.addLayout(stats_layout)

        # Панель инструментов — кнопки только при наличии прав
        toolbar = QHBoxLayout()

        # Кнопка "Добавить ТО" — только при наличии права create_maintenance
        if self.current_user and self.current_user.has_permission('create_maintenance'):
            self.add_btn = QPushButton("➕ Добавить ТО")
            self.add_btn.setMinimumHeight(45)
            self.add_btn.clicked.connect(self.add_maintenance)
            toolbar.addWidget(self.add_btn)

        # Кнопка "Отметить выполненным" — только при наличии права edit_maintenance
        if self.current_user and self.current_user.has_permission('edit_maintenance'):
            self.complete_btn = QPushButton("✅ Отметить выполненным")
            self.complete_btn.setMinimumHeight(45)
            self.complete_btn.clicked.connect(self.complete_maintenance)
            toolbar.addWidget(self.complete_btn)

        # Кнопка "Отменить" — только при наличии права edit_maintenance
        if self.current_user and self.current_user.has_permission('edit_maintenance'):
            self.cancel_btn = QPushButton("❌ Отменить")
            self.cancel_btn.setMinimumHeight(45)
            self.cancel_btn.clicked.connect(self.cancel_maintenance)
            toolbar.addWidget(self.cancel_btn)

        # Кнопка "Удалить" — только при наличии права delete_maintenance
        if self.current_user and self.current_user.has_permission('delete_maintenance'):
            self.delete_btn = QPushButton("🗑️ Удалить")
            self.delete_btn.setObjectName("delete_btn")
            self.delete_btn.setMinimumHeight(45)
            self.delete_btn.clicked.connect(self.delete_maintenance)
            toolbar.addWidget(self.delete_btn)

        toolbar.addStretch()

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(self.refresh_btn)

        layout.addLayout(toolbar)

        # Таблица
        self.table = QTableWidget()
        self.table.setObjectName("maintenance_table")
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Автомобиль", "Тип ТО", "Дата", "Пробег",
            "Следующее ТО", "Стоимость (руб.)", "Кто выполнял", "Статус"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(350)
        layout.addWidget(self.table)

        # Сигналы — подключаем только существующие кнопки
        #if hasattr(self, 'add_btn'):
        #   self.add_btn.clicked.connect(self.add_maintenance)
        #if hasattr(self, 'complete_btn'):
        #    self.complete_btn.clicked.connect(self.complete_maintenance)
        #if hasattr(self, 'cancel_btn'):
        #    self.cancel_btn.clicked.connect(self.cancel_maintenance)
        #if hasattr(self, 'delete_btn'):
        #    self.delete_btn.clicked.connect(self.delete_maintenance)
        #self.refresh_btn.clicked.connect(self.load_data)

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
        """Загрузка данных о ТО."""
        self.all_maintenance = self.controller.get_all_maintenance()
        self.display_maintenance(self.all_maintenance)
        self.update_stats()

    def display_maintenance(self, records):
        """Отображение записей ТО в таблице."""
        self.table.setRowCount(len(records))
        for row, m in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(str(m["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(m["car_info"]))
            self.table.setItem(row, 2, QTableWidgetItem(m["maintenance_type"]))
            self.table.setItem(row, 3, QTableWidgetItem(m["maintenance_date"]))
            self.table.setItem(row, 4, QTableWidgetItem(f"{m['mileage']} км" if m['mileage'] else "N/A"))
            self.table.setItem(row, 5,
                               QTableWidgetItem(m["next_maintenance_date"] if m["next_maintenance_date"] else "N/A"))
            self.table.setItem(row, 6, QTableWidgetItem(str(m["cost"]) if m["cost"] else "0"))
            self.table.setItem(row, 7, QTableWidgetItem(m["performed_by"]))

            status_item = QTableWidgetItem(m["status"])
            if m["status"] == "Выполнено":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif m["status"] == "Запланировано":
                status_item.setForeground(Qt.GlobalColor.darkYellow)
            elif m["status"] == "Отменено":
                status_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 8, status_item)
        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.table, min_height=40)

    def update_stats(self):
        """Обновление карточек статистики."""
        stats = self.controller.get_statistics()

        for card, key, suffix in [
            (self.total_card, "total_count", " "),
            (self.scheduled_card, "scheduled_count", " "),
            (self.completed_card, "total_cost", " руб.")
        ]:
            labels = card.findChildren(QLabel)
            if len(labels) >= 2:
                value = stats.get(key, 0)
                labels[1].setText(f"{value}{suffix}")

    def add_maintenance(self):
        """Добавление новой записи ТО."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('create_maintenance'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для добавления записей ТО")
            return

        dialog = MaintenanceDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            result = self.controller.add_maintenance(
                car_id=data["car_id"],
                maintenance_type=data["maintenance_type"],
                maintenance_date=data["maintenance_date"],
                description=data["description"],
                mileage=data["mileage"],
                next_mileage=data["next_mileage"],
                next_maintenance_date=data["next_maintenance_date"],
                cost=data["cost"],
                performed_by=data["performed_by"]
            )
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "Запись ТО успешно добавлена.")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def complete_maintenance(self):
        """Отметить ТО как выполненное."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('edit_maintenance'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для изменения статуса ТО")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите запись ТО")
            return
        row = selected[0].row()
        maintenance_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 8).text()

        if status == "Выполнено":
            QMessageBox.warning(self, "Внимание", "ТО уже выполнено")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Отметить ТО №{maintenance_id} как выполненное?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.complete_maintenance(maintenance_id)
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "ТО отмечено как выполненное")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def cancel_maintenance(self):
        """Отмена ТО."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('edit_maintenance'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для отмены ТО")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите запись ТО")
            return
        row = selected[0].row()
        maintenance_id = int(self.table.item(row, 0).text())
        status = self.table.item(row, 8).text()

        if status == "Выполнено":
            QMessageBox.warning(self, "Внимание", "Нельзя отменить выполненное ТО")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Отменить ТО №{maintenance_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.cancel_maintenance(maintenance_id)
            if result["success"]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def delete_maintenance(self):
        """Удаление записи ТО."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('delete_maintenance'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для удаления записей ТО")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите запись ТО")
            return
        row = selected[0].row()
        maintenance_id = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить запись ТО №{maintenance_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.delete_maintenance(maintenance_id)
            if result["success"]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)