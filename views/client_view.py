from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QDialog, QFormLayout, QLineEdit, QMessageBox,
                             QHeaderView, QAbstractItemView, QLabel)
from PyQt6.QtCore import Qt
from database import SessionLocal
from controllers.client_controller import ClientController


class ClientDialog(QDialog):
    """Диалог добавления/редактирования клиента."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление клиента")
        self.resize(450, 320)

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(40)
        self.series_input = QLineEdit()
        self.series_input.setMaxLength(4)
        self.series_input.setMinimumHeight(40)
        self.number_input = QLineEdit()
        self.number_input.setMaxLength(6)
        self.number_input.setMinimumHeight(40)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+79001234567")
        self.phone_input.setMinimumHeight(40)
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(40)

        layout.addRow("👤 ФИО:", self.name_input)
        layout.addRow("📄 Серия паспорта:", self.series_input)
        layout.addRow("📄 Номер паспорта:", self.number_input)
        layout.addRow("📞 Телефон:", self.phone_input)
        layout.addRow("📧 Email (необяз.):", self.email_input)

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
            "full_name": self.name_input.text(),
            "passport_series": self.series_input.text(),
            "passport_number": self.number_input.text(),
            "phone": self.phone_input.text(),
            "email": self.email_input.text()
        }


class ClientWidget(QWidget):
    """Виджет управления клиентами с поиском по ФИО."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.controller = ClientController(self.db)
        self.all_clients = []
        self.current_user = current_user  # Получаем текущего пользователя

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок раздела
        header_label = QLabel("👥 Управление клиентами")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # Панель поиска
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Поиск по ФИО:")
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Введите фамилию, имя или отчество...")
        self.search_input.textChanged.connect(self.filter_clients)
        self.search_input.setMaximumWidth(400)
        self.search_input.setMinimumHeight(40)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # Панель инструментов — кнопки создаются ВСЕГДА, проверка прав при клике
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить клиента")
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_client)

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.setMinimumHeight(45)
        self.delete_btn.clicked.connect(self.delete_client)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_data)

        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_btn)
        layout.addLayout(toolbar)

        # Таблица
        self.table = QTableWidget()
        self.table.setObjectName("client_table")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "ФИО", "Паспорт", "Телефон", "Email"
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        self.all_clients = self.controller.get_all_clients()
        self.display_clients(self.all_clients)

    def display_clients(self, clients):
        self.table.setRowCount(len(clients))
        for row, c in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(str(c["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(c["full_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(c["passport"]))
            self.table.setItem(row, 3, QTableWidgetItem(c["phone"]))
            self.table.setItem(row, 4, QTableWidgetItem(c["email"]))
        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.table, min_height=40)

    def filter_clients(self, search_text):
        """Фильтрация клиентов по ФИО."""
        search_text = search_text.lower().strip()
        if not search_text:
            self.display_clients(self.all_clients)
            return

        filtered = [
            client for client in self.all_clients
            if search_text in client["full_name"].lower()
        ]
        self.display_clients(filtered)

    def add_client(self):
        # Проверка прав перед действием
        if self.current_user and not self.current_user.has_permission('create_client'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для добавления клиентов")
            return

        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            result = self.controller.add_client(
                data["full_name"], data["passport_series"],
                data["passport_number"], data["phone"], data["email"]
            )
            if result["success"]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def delete_client(self):
        # Проверка прав перед действием
        if self.current_user and not self.current_user.has_permission('delete_client'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для удаления клиентов")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите клиента для удаления")
            return
        row = selected[0].row()
        client_id = int(self.table.item(row, 0).text())
        client_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Подтверждение", f"Удалить клиента {client_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.delete_client(client_id)
            if result["success"]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)