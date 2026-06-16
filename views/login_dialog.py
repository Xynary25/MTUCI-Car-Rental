from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from database import SessionLocal
from utils.auth_service import AuthService
from models.user import User
import logging

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """Диалог авторизации с темным градиентным фоном."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoRent Pro | Вход в систему")
        self.setFixedSize(550, 750)
        self.setModal(True)

        self.db = SessionLocal()
        self.auth_service = AuthService(self.db)
        self.current_user = None

        # Устанавливаем темный градиентный фон для всего окна
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F172A, 
                    stop:0.5 #1E293B, 
                    stop:1 #0F172A);
            }
        """)

        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса авторизации."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(25)

        # Логотип и заголовок
        logo_label = QLabel("🚗 AutoRent Pro")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setObjectName("login_logo")
        logo_label.setStyleSheet("""
            QLabel#login_logo {
                font-size: 36px;
                font-weight: bold;
                color: #60A5FA;
                padding: 10px;
            }
        """)
        main_layout.addWidget(logo_label)

        subtitle_label = QLabel("Система управления арендой автомобилей")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #94A3B8;
                padding-bottom: 20px;
            }
        """)
        main_layout.addWidget(subtitle_label)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #475569; max-height: 2px;")
        main_layout.addWidget(separator)

        # Поле логина
        login_label = QLabel(" Логин")
        login_label.setStyleSheet("color: #CBD5E1; font-size: 13px; font-weight: bold;")
        main_layout.addWidget(login_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин")
        self.username_input.setMinimumHeight(50)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(15, 23, 42, 0.8);
                border: 2px solid #3B82F6;
                border-radius: 12px;
                padding: 12px 18px;
                color: #E2E8F0;
                font-size: 15px;
                selection-background-color: #3B82F6;
                selection-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #60A5FA;
                background-color: rgba(15, 23, 42, 0.95);
            }
            QLineEdit::placeholder {
                color: #64748B;
            }
        """)
        main_layout.addWidget(self.username_input)

        # Поле пароля
        password_label = QLabel("🔒 Пароль")
        password_label.setStyleSheet("color: #CBD5E1; font-size: 13px; font-weight: bold;")
        main_layout.addWidget(password_label)

        # Создаем горизонтальный layout для пароля и кнопки глаза
        password_layout = QHBoxLayout()
        password_layout.setSpacing(10)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(50)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(15, 23, 42, 0.8);
                border: 2px solid #3B82F6;
                border-radius: 12px;
                padding: 12px 18px;
                color: #E2E8F0;
                font-size: 15px;
                selection-background-color: #3B82F6;
                selection-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #60A5FA;
                background-color: rgba(15, 23, 42, 0.95);
            }
            QLineEdit::placeholder {
                color: #64748B;
            }
        """)
        self.password_input.returnPressed.connect(self.check_login)
        password_layout.addWidget(self.password_input, stretch=1)

        # Кнопка показа/скрытия пароля
        self.show_password_btn = QPushButton("👁️")
        self.show_password_btn.setFixedSize(50, 50)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(15, 23, 42, 0.8);
                border: 2px solid #3B82F6;
                border-radius: 12px;
                color: #E2E8F0;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(30, 41, 59, 0.9);
                border: 2px solid #60A5FA;
            }
        """)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)

        main_layout.addLayout(password_layout)

        # Кнопка входа
        self.login_btn = QPushButton("🚀 Войти в систему")
        self.login_btn.setMinimumHeight(55)
        self.login_btn.setObjectName("login_btn")
        self.login_btn.setStyleSheet("""
            QPushButton#login_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 17px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton#login_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60A5FA, stop:1 #3B82F6);
            }
            QPushButton#login_btn:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563EB, stop:1 #1D4ED8);
            }
        """)
        self.login_btn.clicked.connect(self.check_login)
        main_layout.addWidget(self.login_btn)

        # Информация о тестовых аккаунтах
        info_label = QLabel(
            "💡 Тестовые аккаунты:\n\n"
            " super / 123123  (Главный Администратор)\n"
            "🔧 admin / admin123            (Администратор)\n"
            "‍💼 manager / manager123        (Менеджер)\n"
            "👤 operator / operator123      (Оператор)"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 12px;
                padding: 20px;
                background-color: rgba(30, 41, 59, 0.6);
                border-radius: 12px;
                border: 1px solid rgba(59, 130, 246, 0.2);
                line-height: 1.8;
            }
        """)
        main_layout.addWidget(info_label)

        main_layout.addStretch()

    def toggle_password_visibility(self):
        """Переключение видимости пароля."""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁️")

    def check_login(self):
        """Проверка учетных данных."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        logger.info("=" * 60)
        logger.info("ПОПЫТКА ВХОДА В СИСТЕМУ")
        logger.info(f"Введенный логин: '{username}'")
        logger.info(f"Введенный пароль: '{'***' if password else 'ПУСТО'}' (длина: {len(password)})")
        logger.info("=" * 60)

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        try:
            logger.info("Вызываем auth_service.authenticate()...")
            # ИСПРАВЛЕНО: не передаем self.db, так как он уже в auth_service
            user = self.auth_service.authenticate(username, password)

            if user:
                logger.info(f"Аутентификация успешна! Пользователь: {user.username}")
                logger.info(f"Роль: {user.role.value}")
                logger.info(f"Активен: {user.is_active}")

                if not user.is_active:
                    logger.warning(f"Попытка входа деактивированного пользователя: {username}")
                    QMessageBox.critical(
                        self, "Аккаунт отключен",
                        "⛔ Ваш аккаунт деактивирован.\n\n"
                        "Обратитесь к администратору системы для восстановления доступа."
                    )
                    return

                self.current_user = user
                logger.info("Вход выполнен успешно!")
                self.accept()
            else:
                logger.error(f"Аутентификация НЕУСПЕШНА для пользователя: {username}")

                # Дополнительная диагностика
                logger.info("Диагностика:")
                user_from_db = self.db.query(User).filter(User.username == username).first()
                if user_from_db:
                    logger.info(f"Пользователь найден в БД: {user_from_db.username}")
                    logger.info(f"Активен: {user_from_db.is_active}")
                    logger.info(f"Соль: {user_from_db.salt}")
                    logger.info(f"Хеш пароля: {user_from_db.password_hash[:20]}...")

                    # Проверяем пароль вручную
                    check_result = user_from_db.check_password(password)
                    logger.info(f"Ручная проверка пароля: {check_result}")

                    # Показываем хеш введенного пароля
                    manual_hash = User._hash_password(password, user_from_db.salt)
                    logger.info(f"Хеш введенного пароля: {manual_hash[:20]}...")
                    logger.info(f"Совпадение хешей: {manual_hash == user_from_db.password_hash}")
                else:
                    logger.info(f"Пользователь '{username}' НЕ НАЙДЕН в БД")

                QMessageBox.critical(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            import traceback
            logger.error(f"Исключение при аутентификации: {str(e)}")
            logger.error(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Ошибка авторизации:\n{str(e)}")

    def get_user(self) -> User:
        """Получить авторизованного пользователя."""
        return self.current_user

    def closeEvent(self, event):
        """Закрытие диалога входа."""
        try:
            if hasattr(self, 'db'):
                self.db.close()
                print("Сессия БД login_dialog закрыта")
            if hasattr(self, 'auth_service'):
                self.auth_service.close()
                print("AuthService login_dialog закрыт")
        except Exception as e:
            print(f"Ошибка при закрытии login_dialog: {e}")
        finally:
            super().closeEvent(event)