from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QDialog, QFormLayout, QComboBox, QDateEdit,
                             QMessageBox, QHeaderView, QAbstractItemView, QLabel, QLineEdit,
                             QFileDialog, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QDate
from database import SessionLocal
from controllers.agreement_controller import AgreementController
from models.client import Client
from models.car import Car
from utils.pdf_generator import generate_agreement_pdf


class ExportDialog(QDialog):
    """Диалог выбора формата экспорта договоров."""

    def __init__(self, count: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор формата экспорта")
        self.resize(450, 250)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Информация о количестве договоров
        if count == 1:
            info_label = QLabel("Выберите формат экспорта договора:")
        else:
            info_label = QLabel(f"Выбрано договоров: {count}\nВыберите формат экспорта:")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 13px; padding: 10px;")
        layout.addWidget(info_label)

        # Группа кнопок
        self.radio_group = QButtonGroup(self)

        # Опция 1: Один файл
        self.single_file_radio = QRadioButton(
            "📄 Один PDF-файл (все договоры на разных страницах)"
        )
        self.single_file_radio.setChecked(True)
        layout.addWidget(self.single_file_radio)
        self.radio_group.addButton(self.single_file_radio, 1)

        # Опция 2: Отдельные файлы
        self.multiple_files_radio = QRadioButton(
            "📁 Отдельные PDF-файлы для каждого договора"
        )
        if count == 1:
            self.multiple_files_radio.setEnabled(False)
        layout.addWidget(self.multiple_files_radio)
        self.radio_group.addButton(self.multiple_files_radio, 2)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("📥 Экспортировать")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_export_mode(self) -> int:
        """Возвращает 1 для одного файла, 2 для нескольких файлов."""
        return self.radio_group.checkedId()

class AgreementDialog(QDialog):
    """Диалог оформления нового договора аренды."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый договор аренды")
        self.resize(450, 350)
        self.db = SessionLocal()

        layout = QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.client_combo = QComboBox()
        self.client_combo.setMinimumHeight(40)
        for c in self.db.query(Client).all():
            self.client_combo.addItem(c.full_name, c.id)

        self.car_combo = QComboBox()
        self.car_combo.setMinimumHeight(40)
        for c in self.db.query(Car).filter(Car.is_available == True).all():
            self.car_combo.addItem(
                f"{c.brand} {c.model} ({c.license_plate}) - {c.daily_rate} руб.",
                c.id
            )
        self.car_combo.currentIndexChanged.connect(self.calculate_cost)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setMinimumHeight(40)
        self.start_date_edit.dateChanged.connect(self.calculate_cost)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(1))
        self.end_date_edit.setMinimumHeight(40)
        self.end_date_edit.dateChanged.connect(self.calculate_cost)

        self.cost_label = QLabel("0 руб.")
        self.cost_label.setObjectName("cost_label")

        layout.addRow("👤 Клиент:", self.client_combo)
        layout.addRow("🚗 Автомобиль:", self.car_combo)
        layout.addRow("📅 Дата начала:", self.start_date_edit)
        layout.addRow("📅 Дата окончания:", self.end_date_edit)
        layout.addRow("💰 Итоговая стоимость:", self.cost_label)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("✅ Оформить")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)

        self.calculate_cost()

    def calculate_cost(self):
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        car = self.db.query(Car).filter(
            Car.id == self.car_combo.currentData()
        ).first()
        if car and end_date > start_date:
            self.cost_label.setText(f"{(end_date - start_date).days * car.daily_rate} руб.")
        else:
            self.cost_label.setText("Некорректные даты")

    def get_data(self):
        return {
            "client_id": self.client_combo.currentData(),
            "car_id": self.car_combo.currentData(),
            "start_date": self.start_date_edit.date().toPyDate(),
            "end_date": self.end_date_edit.date().toPyDate()
        }

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


class AgreementWidget(QWidget):
    """Виджет раздела «Договоры аренды»."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.controller = AgreementController(self.db)
        self.all_agreements = []
        self.current_user = current_user  # Получаем текущего пользователя

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок раздела
        header_label = QLabel("📝 Договоры аренды")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # Панель поиска
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Поиск по клиенту или авто...")
        self.search_input.textChanged.connect(self.filter_agreements)
        self.search_input.setMaximumWidth(400)
        self.search_input.setMinimumHeight(40)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # Панель инструментов — кнопки создаются ВСЕГДА, проверка прав при клике
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Новый договор")
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_agreement)

        self.complete_btn = QPushButton("✅ Завершить договор")
        self.complete_btn.setMinimumHeight(45)
        self.complete_btn.clicked.connect(self.complete_agreement)

        self.print_btn = QPushButton("🖨️ Печать PDF")
        self.print_btn.setMinimumHeight(45)
        self.print_btn.clicked.connect(self.print_agreement)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_data)

        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.complete_btn)
        toolbar.addWidget(self.print_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_btn)
        layout.addLayout(toolbar)

        # Подсказка
        hint_label = QLabel("💡 Используйте Ctrl+клик или Shift+клик для выбора нескольких договоров.")
        hint_label.setObjectName("hint_label")
        layout.addWidget(hint_label)

        # Таблица
        self.table = QTableWidget()
        self.table.setObjectName("agreement_table")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Клиент", "Автомобиль", "Начало", "Окончание",
            "Стоимость (руб.)", "Статус"
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
        self.all_agreements = self.controller.get_all_agreements()
        self.display_agreements(self.all_agreements)

    def display_agreements(self, agreements):
        self.table.setRowCount(len(agreements))
        for row, a in enumerate(agreements):
            self.table.setItem(row, 0, QTableWidgetItem(str(a["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(a["client_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(a["car_info"]))
            self.table.setItem(row, 3, QTableWidgetItem(a["start_date"]))
            self.table.setItem(row, 4, QTableWidgetItem(a["end_date"]))
            self.table.setItem(row, 5, QTableWidgetItem(str(a["total_cost"])))

            status_item = QTableWidgetItem(a["status"])
            if a["status"] == "active":
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif a["status"] == "completed":
                status_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 6, status_item)
        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.table, min_height=40)

    def filter_agreements(self, text):
        text = text.lower()
        if not text:
            self.display_agreements(self.all_agreements)
            return
        filtered = [
            a for a in self.all_agreements
            if text in a["client_name"].lower() or text in a["car_info"].lower()
        ]
        self.display_agreements(filtered)

    def add_agreement(self):
        # Проверка прав перед действием
        if self.current_user and not self.current_user.has_permission('create_agreement'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для создания договоров")
            return

        dialog = AgreementDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            result = self.controller.create_agreement(
                data["client_id"], data["car_id"],
                data["start_date"], data["end_date"]
            )
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "Договор оформлен.")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def complete_agreement(self):
        # Проверка прав перед действием
        if self.current_user and not self.current_user.has_permission('edit_agreement'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для завершения договоров")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите договор")
            return
        row = selected[0].row()
        if self.table.item(row, 6).text() != "active":
            QMessageBox.warning(self, "Внимание", "Можно завершить только активный договор.")
            return
        if QMessageBox.question(
            self, "Подтверждение", "Завершить договор?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            result = self.controller.complete_agreement(
                int(self.table.item(row, 0).text())
            )
            if result["success"]:
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def print_agreement(self):
        """Экспорт договоров в PDF с учетом штрафов."""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "Внимание", "Выберите один или несколько договоров для экспорта")
            return

        # Собираем данные выбранных договоров
        selected_agreements = []
        all_penalties_list = []

        for row in sorted(selected_rows):
            a_id = int(self.table.item(row, 0).text())
            a_data = next((a for a in self.all_agreements if a["id"] == a_id), None)
            if a_data:
                # Получаем штрафы для этого договора из БД
                from database import SessionLocal
                from models.penalty import Penalty
                db = SessionLocal()
                try:
                    penalties = db.query(Penalty).filter(
                        Penalty.agreement_id == a_id
                    ).all()

                    penalties_data = [
                        {
                            "penalty_type": p.penalty_type.value,
                            "description": p.description or " ",
                            "amount": p.amount,
                            "is_paid": p.is_paid,
                            "status": p.status.value
                        }
                        for p in penalties
                    ]

                    all_penalties_list.append(penalties_data)
                finally:
                    db.close()

                selected_agreements.append(a_data)

        if not selected_agreements:
            return

        # Диалог выбора формата экспорта
        export_dialog = ExportDialog(len(selected_agreements), self)
        if export_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        export_mode = export_dialog.get_export_mode()

        if export_mode == 1:
            # Один файл со всеми договорами
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Сохранить договоры", "Agreements.pdf", "PDF Files (*.pdf)"
            )
            if filepath:
                try:
                    from utils.pdf_generator import generate_multiple_agreements_pdf

                    result = generate_multiple_agreements_pdf(
                        selected_agreements,
                        all_penalties_list,
                        filepath
                    )

                    if result.get("success"):
                        QMessageBox.information(
                            self, "Успех",
                            f"Экспортировано {len(selected_agreements)} договор(ов) в файл:\n{filepath}"
                        )
                    else:
                        error_msg = result.get("error", "Неизвестная ошибка")
                        QMessageBox.critical(self, "Ошибка", f"Не удалось создать PDF:\n{error_msg}")
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Ошибка генерации PDF: {error_details}")
                    QMessageBox.critical(self, "Ошибка", f"Не удалось создать PDF:\n{str(e)}\n\n{error_details}")

        elif export_mode == 2:
            # Отдельные файлы для каждого договора
            folder_path = QFileDialog.getExistingDirectory(
                self, "Выберите папку для сохранения договоров"
            )
            if folder_path:
                try:
                    from utils.pdf_generator import generate_agreement_pdf
                    import os

                    exported_count = 0
                    for i, a_data in enumerate(selected_agreements):
                        filename = f"Agreement_{a_data['id']}_{a_data['client_name'].replace(' ', '_')}.pdf"
                        filepath = os.path.join(folder_path, filename)

                        penalties_for_this = all_penalties_list[i] if i < len(all_penalties_list) else []

                        result = generate_agreement_pdf(
                            a_data,
                            penalties_for_this,
                            filepath
                        )

                        if result.get("success"):
                            exported_count += 1

                    QMessageBox.information(
                        self, "Успех",
                        f"Экспортировано {exported_count} договор(ов) в папку:\n{folder_path}"
                    )
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Ошибка генерации PDF: {error_details}")
                    QMessageBox.critical(self, "Ошибка", f"Не удалось создать PDF:\n{str(e)}\n\n{error_details}")

    def highlight_agreement(self, agreement_id: int):
        """Выделить договор в таблице."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.text()) == agreement_id:
                self.table.selectRow(row)
                self.table.scrollToItem(
                    self.table.item(row, 0),
                    QAbstractItemView.ScrollHint.PositionAtCenter
                )

                QMessageBox.information(
                    self.parent() if self.parent() else self,
                    "Договор",
                    f"Договор #{agreement_id}\n\n"
                    f"Клиент: {self.all_agreements[row]['client_name']}\n"
                    f"Автомобиль: {self.all_agreements[row]['car_info']}\n"
                    f"Статус: {self.all_agreements[row]['status']}"
                )
                break

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)