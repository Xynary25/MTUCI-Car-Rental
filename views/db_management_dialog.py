from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel,
                             QGroupBox, QMessageBox, QFrame, QApplication)
from PyQt6.QtCore import Qt
from utils.db_manager import (
    delete_database,
    create_empty_database,
    create_database_with_test_data,
    restore_from_backup
)


class DBManagementDialog(QDialog):
    """Диалог управления базой данных (после закрытия приложения)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🗄️ Управление базой данных")
        self.resize(700, 500)
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        header_label = QLabel("️ Управление базой данных")
        header_label.setObjectName("section_header")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(header_label)

        # Предупреждение
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 2px solid #F59E0B;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        warning_layout = QVBoxLayout(warning_frame)

        warning_label = QLabel(
            "⚠️ ВНИМАНИЕ!\n\n"
            "Вы находитесь в режиме управления базой данных.\n"
            "Все операции необратимы и могут привести к потере данных!\n"
            "Рекомендуется создать резервную копию перед выполнением операций."
        )
        warning_label.setWordWrap(True)
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setStyleSheet("font-size: 13px; color: #92400E;")
        warning_layout.addWidget(warning_label)

        layout.addWidget(warning_frame)

        # Группа кнопок управления
        buttons_group = QGroupBox("🔧 Операции с базой данных")
        buttons_layout = QVBoxLayout(buttons_group)
        buttons_layout.setSpacing(15)

        # Кнопка: Создать пустую БД
        self.create_empty_btn = QPushButton("📄 Создать пустую базу данных")
        self.create_empty_btn.setMinimumHeight(50)
        self.create_empty_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.create_empty_btn.clicked.connect(self.create_empty_db)
        buttons_layout.addWidget(self.create_empty_btn)

        # Кнопка: Создать БД с тестовыми данными
        self.create_test_btn = QPushButton("🧪 Создать базу данных с тестовыми данными")
        self.create_test_btn.setMinimumHeight(50)
        self.create_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.create_test_btn.clicked.connect(self.create_test_db)
        buttons_layout.addWidget(self.create_test_btn)

        # Кнопка: Восстановить из бэкапа
        self.restore_btn = QPushButton("♻️ Восстановить из резервной копии")
        self.restore_btn.setMinimumHeight(50)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
        """)
        self.restore_btn.clicked.connect(self.restore_db)
        buttons_layout.addWidget(self.restore_btn)

        # Кнопка: Удалить БД
        self.delete_btn = QPushButton("🗑️ Удалить базу данных")
        self.delete_btn.setMinimumHeight(50)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_db)
        buttons_layout.addWidget(self.delete_btn)

        layout.addWidget(buttons_group)

        # Кнопка открытия главного окна
        self.open_main_btn = QPushButton("🚀 Открыть главное окно приложения")
        self.open_main_btn.setMinimumHeight(50)
        self.open_main_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B5CF6;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        """)
        self.open_main_btn.clicked.connect(self.open_main_window)
        layout.addWidget(self.open_main_btn)

        # Кнопка закрытия
        close_btn = QPushButton("❌ Закрыть и выйти")
        close_btn.setMinimumHeight(45)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def create_empty_db(self):
        """Создание пустой базы данных."""
        reply = QMessageBox.warning(
            self, "Подтверждение",
            "️ ВНИМАНИЕ!\n\n"
            "Все текущие данные будут УДАЛЕНЫ!\n"
            "Будет создана пустая база данных только со структурой таблиц.\n\n"
            "Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = create_empty_database()
            if result["success"]:
                QMessageBox.information(self, "Успех", result["message"])
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def create_test_db(self):
        """Создание базы данных с тестовыми данными."""
        reply = QMessageBox.warning(
            self, "Подтверждение",
            "⚠️ ВНИМАНИЕ!\n\n"
            "Все текущие данные будут УДАЛЕНЫ!\n"
            "Будет создана база данных с тестовыми пользователями и данными.\n\n"
            "Тестовые аккаунты:\n"
            "• superadmin / superadmin123\n"
            "• admin / admin123\n"
            "• manager / manager123\n"
            "• operator / operator123\n\n"
            "Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = create_database_with_test_data()
            if result["success"]:
                QMessageBox.information(self, "Успех", result["message"])
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def restore_db(self):
        """Восстановление базы данных из резервной копии."""
        from PyQt6.QtWidgets import QFileDialog

        backup_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл резервной копии",
            "./backups",
            "Database Files (*.db);;All Files (*)"
        )

        if backup_path:
            reply = QMessageBox.warning(
                self, "Подтверждение",
                "️ ВНИМАНИЕ!\n\n"
                "Все текущие данные будут ЗАМЕНЕНЫ данными из резервной копии!\n\n"
                f"Файл бэкапа: {backup_path}\n\n"
                "Продолжить?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                result = restore_from_backup(backup_path)
                if result["success"]:
                    QMessageBox.information(self, "Успех", result["message"])
                else:
                    QMessageBox.critical(self, "Ошибка", result["error"])

    def delete_db(self):
        """Удаление базы данных."""
        reply = QMessageBox.critical(
            self, "КРИТИЧЕСКОЕ ДЕЙСТВИЕ",
            "🚨 ВНИМАНИЕ! ЭТО ДЕЙСТВИЕ НЕОБРАТИМО! 🚨\n\n"
            "База данных будет ПОЛНОСТЬЮ УДАЛЕНА!\n"
            "Все данные будут потеряны без возможности восстановления!\n\n"
            "Для продолжения введите: УДАЛИТЬ",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        if reply == QMessageBox.StandardButton.Ok:
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(
                self,
                "Подтверждение удаления",
                "Введите 'УДАЛИТЬ' для подтверждения:"
            )

            if ok and text == "УДАЛИТЬ":
                result = delete_database()
                if result["success"]:
                    QMessageBox.information(self, "Успех", result["message"])
                else:
                    QMessageBox.critical(self, "Ошибка", result["error"])
            else:
                QMessageBox.information(self, "Отмена", "Удаление отменено")

    def open_main_window(self):
        """Открытие главного окна приложения."""
        from views.login_dialog import LoginDialog

        # Показываем окно входа
        login_dialog = LoginDialog()
        if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
            new_user = login_dialog.get_user()
            if new_user:
                # Сохраняем данные пользователя во временный файл
                from utils.db_operation_flag import set_db_operation_pending
                # Используем специальный флаг "login" чтобы main.py знал что нужно показать вход
                # Но мы уже вошли, поэтому просто принимаем диалог
                self.accept()  # Возвращает DialogCode.Accepted
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось получить данные пользователя")
        else:
            QMessageBox.information(self, "Отмена", "Вход отменён")