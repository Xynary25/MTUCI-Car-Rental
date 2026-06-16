from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QFileDialog, QMessageBox, QHeaderView, QAbstractItemView,
                             QGroupBox, QLabel, QMainWindow, QScrollArea, QFrame, QApplication)
from PyQt6.QtCore import Qt
from database import SessionLocal
from models.audit_log import AuditLog
from utils.system_utils import create_database_backup



class AuditWidget(QWidget):
    """Виджет раздела «Безопасность и аудит»."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.current_user = current_user

        # Главный layout с прокруткой
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Создаем scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Контейнер для содержимого
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок раздела
        header_label = QLabel("🛡️ Безопасность и аудит")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # Проверка прав на просмотр аудита
        if self.current_user and not self.current_user.has_permission('view_audit'):
            no_access_label = QLabel(
                " У вас нет прав для просмотра журнала аудита.\n"
                "Обратитесь к администратору системы."
            )
            no_access_label.setObjectName("no_access_label")
            no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_access_label.setStyleSheet("font-size: 16px; color: #64748B; padding: 40px;")
            layout.addWidget(no_access_label)
            layout.addStretch()
            scroll.setWidget(container)
            main_layout.addWidget(scroll)
            return

        # Группа резервного копирования
        if self.current_user and self.current_user.has_permission('backup_database'):
            backup_group = QGroupBox("💾 Резервное копирование")
            backup_layout = QVBoxLayout(backup_group)

            backup_info = QLabel(
                "Регулярное резервное копирование обеспечивает сохранность данных "
                "в случае сбоев оборудования или программных ошибок."
            )
            backup_info.setWordWrap(True)
            backup_layout.addWidget(backup_info)

            self.backup_btn = QPushButton(" Создать резервную копию базы данных")
            self.backup_btn.setMinimumHeight(45)
            self.backup_btn.clicked.connect(self.create_backup)
            backup_layout.addWidget(self.backup_btn)

            layout.addWidget(backup_group)

        # Группа журнала аудита
        audit_group = QGroupBox(" Журнал аудита действий")
        audit_layout = QVBoxLayout(audit_group)

        self.table = QTableWidget()
        self.table.setObjectName("audit_table")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Время", "Действие", "Сущность", "ID записи", "Описание"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumHeight(300)
        audit_layout.addWidget(self.table)

        self.refresh_btn = QPushButton("🔄 Обновить журнал")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_audit_log)
        audit_layout.addWidget(self.refresh_btn)

        layout.addWidget(audit_group)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self.load_audit_log()

        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.table, min_height=40)

    def create_backup(self):
        """Запуск процедуры резервного копирования."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('backup_database'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для создания резервных копий")
            return

        backup_dir = QFileDialog.getExistingDirectory(
            self, "Выберите папку для резервной копии"
        )
        if backup_dir:
            reply = QMessageBox.question(
                self, "Подтверждение", "Создать резервную копию базы данных?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                result = create_database_backup(backup_dir, self.db)
                if result["success"]:
                    QMessageBox.information(
                        self, "Успех", f"Резервная копия создана:\n{result['path']}"
                    )
                    self.load_audit_log()
                else:
                    QMessageBox.critical(self, "Ошибка", result["error"])

    def load_audit_log(self):
        """Загрузка записей из журнала аудита."""
        try:
            logs = self.db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
            self.table.setRowCount(len(logs))

            for row, log in enumerate(logs):
                self.table.setItem(row, 0, QTableWidgetItem(
                    log.timestamp.strftime("%d.%m.%Y %H:%M:%S")
                ))
                self.table.setItem(row, 1, QTableWidgetItem(log.action_type.value))
                self.table.setItem(row, 2, QTableWidgetItem(log.entity_name))
                self.table.setItem(row, 3, QTableWidgetItem(
                    str(log.entity_id) if log.entity_id else "N/A"
                ))
                self.table.setItem(row, 4, QTableWidgetItem(log.description))

            from utils.table_utils import auto_resize_table_rows
            auto_resize_table_rows(self.table, min_height=40)
        except Exception as e:
            print(f"Ошибка загрузки журнала аудита: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить журнал:\n{str(e)}")

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)