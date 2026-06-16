from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QHBoxLayout)
from PyQt6.QtCore import Qt
from database import SessionLocal
from utils.auth_service import AuthService


class ChangePasswordDialog(QDialog):
    """Диалог смены пароля."""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Смена пароля")
        self.resize(400, 300)
        self.setModal(True)

        self.db = SessionLocal()
        self.auth_service = AuthService(self.db)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🔐 Смена пароля")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.old_password = QLineEdit()
        self.old_password.setPlaceholderText("Текущий пароль")
        self.old_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.old_password.setMinimumHeight(40)
        layout.addWidget(self.old_password)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Новый пароль (мин. 6 символов)")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setMinimumHeight(40)
        layout.addWidget(self.new_password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Подтвердите новый пароль")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setMinimumHeight(40)
        layout.addWidget(self.confirm_password)

        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.change_password)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def change_password(self):
        old_pass = self.old_password.text()
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()

        if not old_pass or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        result = self.auth_service.change_password(self.user, old_pass, new_pass)

        if result["success"]:
            QMessageBox.information(self, "Успех", "Пароль успешно изменён!")
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", result["error"])

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)