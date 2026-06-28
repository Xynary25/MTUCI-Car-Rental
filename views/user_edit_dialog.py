from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QComboBox, QCheckBox,
                             QGroupBox, QScrollArea, QFrame, QGridLayout, QWidget)
from PyQt6.QtCore import Qt
from models.user import User, UserRole
from utils.auth_service import AuthService
from database import SessionLocal
import logging

logger = logging.getLogger(__name__)


class UserEditDialog(QDialog):
    """Диалог создания/редактирования пользователя."""

    def __init__(self, user: User = None, current_admin: User = None, parent=None):
        super().__init__(parent)
        self.user = user
        self.current_admin = current_admin
        self.is_edit_mode = user is not None
        self.is_superadmin_edit = user and user.username == "superadmin"

        self.db = SessionLocal()
        self.auth_service = AuthService(self.db)

        title = "Редактирование пользователя" if self.is_edit_mode else "Новый пользователь"
        if self.is_superadmin_edit:
            title += " (Главный Администратор)"

        self.setWindowTitle(title)
        self.resize(600, 700)
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title_label = QLabel("✏️ Редактирование пользователя" if self.is_edit_mode else "➕ Новый пользователь")
        if self.is_superadmin_edit:
            title_label.setText("✏️ Редактирование Главного Администратора")
        title_label.setObjectName("section_header")
        layout.addWidget(title_label)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # === Группа: Основные данные ===
        main_group = QGroupBox("👤 Основные данные")
        main_layout = QVBoxLayout(main_group)

        # Логин
        username_layout = QHBoxLayout()
        username_label = QLabel("Логин:")
        username_label.setMinimumWidth(120)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите логин (латиница, цифры)")
        self.username_input.setMinimumHeight(40)
        if self.is_superadmin_edit:
            self.username_input.setEnabled(False)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        main_layout.addLayout(username_layout)

        # ФИО
        fullname_layout = QHBoxLayout()
        fullname_label = QLabel("ФИО:")
        fullname_label.setMinimumWidth(120)
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Иванов Иван Иванович")
        self.fullname_input.setMinimumHeight(40)
        fullname_layout.addWidget(fullname_label)
        fullname_layout.addWidget(self.fullname_input)
        main_layout.addLayout(fullname_layout)

        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        email_label.setMinimumWidth(120)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("user@example.com")
        self.email_input.setMinimumHeight(40)
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        main_layout.addLayout(email_layout)

        content_layout.addWidget(main_group)

        # === Группа: Паспортные данные (для клиентов) ===
        if not self.is_edit_mode or self.user.role == UserRole.OPERATOR or self.user.role == UserRole.USER:
            passport_group = QGroupBox("📄 Паспортные данные")
            passport_layout = QGridLayout(passport_group)
            passport_layout.setSpacing(10)

            # Серия и номер
            passport_series_label = QLabel("Серия:")
            self.passport_series_input = QLineEdit()
            self.passport_series_input.setMaxLength(4)
            self.passport_series_input.setPlaceholderText("4501")
            self.passport_series_input.setMinimumHeight(40)

            passport_number_label = QLabel("Номер:")
            self.passport_number_input = QLineEdit()
            self.passport_number_input.setMaxLength(6)
            self.passport_number_input.setPlaceholderText("123456")
            self.passport_number_input.setMinimumHeight(40)

            passport_layout.addWidget(passport_series_label, 0, 0)
            passport_layout.addWidget(self.passport_series_input, 0, 1)
            passport_layout.addWidget(passport_number_label, 0, 2)
            passport_layout.addWidget(self.passport_number_input, 0, 3)

            # Дата выдачи
            passport_issue_date_label = QLabel("Дата выдачи:")
            self.passport_issue_date_input = QLineEdit()
            self.passport_issue_date_input.setPlaceholderText("дд.мм.гггг")
            self.passport_issue_date_input.setMinimumHeight(40)

            passport_layout.addWidget(passport_issue_date_label, 1, 0)
            passport_layout.addWidget(self.passport_issue_date_input, 1, 1, 1, 3)

            # Кем выдан
            passport_issue_place_label = QLabel("Кем выдан:")
            self.passport_issue_place_input = QLineEdit()
            self.passport_issue_place_input.setPlaceholderText("УФМС России по г. Москве")
            self.passport_issue_place_input.setMinimumHeight(40)

            passport_layout.addWidget(passport_issue_place_label, 2, 0)
            passport_layout.addWidget(self.passport_issue_place_input, 2, 1, 1, 3)

            content_layout.addWidget(passport_group)

            # Заполняем данные при редактировании (БЕЗОПАСНАЯ ВЕРСИЯ)
            if self.is_edit_mode:
                from models.client import Client
                client = self.db.query(Client).filter(Client.full_name == self.user.full_name).first()
                if client:
                    self.passport_series_input.setText(client.passport_series or "")
                    self.passport_number_input.setText(client.passport_number or "")
                    # БЕЗОПАСНАЯ проверка наличия атрибута
                    if hasattr(client, 'passport_issue_date') and client.passport_issue_date:
                        try:
                            self.passport_issue_date_input.setText(
                                client.passport_issue_date.strftime("%d.%m.%Y")
                            )
                        except:
                            pass
                    if hasattr(client, 'passport_issue_place'):
                        self.passport_issue_place_input.setText(client.passport_issue_place or "")

        # === Группа: Безопасность ===
        security_group = QGroupBox("🔐 Безопасность")
        security_layout = QVBoxLayout(security_group)

        # Пароль
        password_layout = QHBoxLayout()
        password_label = QLabel("Пароль:")
        password_label.setMinimumWidth(120)
        self.password_input = QLineEdit()
        placeholder = "Новый пароль (мин. 6 символов)" if self.is_edit_mode else "Пароль (мин. 6 символов)"
        self.password_input.setPlaceholderText(placeholder)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input, stretch=1)

        # Кнопка показа пароля
        self.show_password_btn = QPushButton("👁️")
        self.show_password_btn.setFixedSize(40, 40)
        self.show_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_btn)

        security_layout.addLayout(password_layout)

        # Подтверждение пароля
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("Подтвердите:")
        confirm_label.setMinimumWidth(120)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Повторите пароль")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(40)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_password_input, stretch=1)

        # Кнопка показа подтверждения пароля
        self.show_confirm_btn = QPushButton("👁️")
        self.show_confirm_btn.setFixedSize(40, 40)
        self.show_confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        self.show_confirm_btn.clicked.connect(self.toggle_confirm_visibility)
        confirm_layout.addWidget(self.show_confirm_btn)

        security_layout.addLayout(confirm_layout)

        # Подсказка
        if self.is_edit_mode:
            password_hint = QLabel("💡 Оставьте поля пустыми при редактировании, чтобы не менять пароль")
            password_hint.setObjectName("hint_label")
            security_layout.addWidget(password_hint)

        content_layout.addWidget(security_group)

        # === Группа: Роль и статус ===
        role_group = QGroupBox("🎭 Роль и статус")
        role_layout = QVBoxLayout(role_group)

        # Роль
        role_combo_layout = QHBoxLayout()
        role_label = QLabel("Роль:")
        role_label.setMinimumWidth(120)
        self.role_combo = QComboBox()

        if self.current_admin and self.current_admin.username == "superadmin":
            self.role_combo.addItems([
                "👑 Главный Администратор (полный доступ)",
                "🔧 Администратор (полный доступ)",
                "👨‍💼 Менеджер (управление договорами)",
                "👤 Оператор (только просмотр и договоры)",
                "👤 Пользователь (базовый доступ)"
            ])
        else:
            self.role_combo.addItems([
                "🔧 Администратор (полный доступ)",
                "👨‍💼 Менеджер (управление договорами)",
                "👤 Оператор (только просмотр и договоры)",
                "👤 Пользователь (базовый доступ)"
            ])

        self.role_combo.setMinimumHeight(40)
        if not self.current_admin or self.current_admin.username != "superadmin":
            if self.is_edit_mode and self.user.id == self.current_admin.id:
                self.role_combo.setEnabled(False)
        role_combo_layout.addWidget(role_label)
        role_combo_layout.addWidget(self.role_combo)
        role_layout.addLayout(role_combo_layout)

        # Статус
        self.active_check = QCheckBox("Активен (может входить в систему)")
        self.active_check.setChecked(True)
        if self.is_superadmin_edit:
            self.active_check.setEnabled(False)
        role_layout.addWidget(self.active_check)

        content_layout.addWidget(role_group)

        # === Группа: Индивидуальные права ===
        permissions_group = QGroupBox("⚙️ Индивидуальные права доступа")
        permissions_layout = QVBoxLayout(permissions_group)

        if self.is_superadmin_edit:
            perm_disabled_label = QLabel("⚠️ Права Главного Администратора не могут быть изменены")
            perm_disabled_label.setStyleSheet("color: #EF4444; font-weight: bold; padding: 10px;")
            permissions_layout.addWidget(perm_disabled_label)
            self.permission_checks = {}
        else:
            permissions_hint = QLabel(
                " Если не выбрано ни одного права — используются права роли по умолчанию.\n"
                "Если выбраны конкретные права — они переопределяют роль."
            )
            permissions_hint.setObjectName("hint_label")
            permissions_hint.setWordWrap(True)
            permissions_layout.addWidget(permissions_hint)

            self.permission_checks = {}
            all_permissions = self.auth_service.get_all_permissions()

            categories = {
                "👁️ Просмотр": [p for p in all_permissions if p.startswith("view_")],
                "➕ Создание": [p for p in all_permissions if p.startswith("create_")],
                "✏️ Редактирование": [p for p in all_permissions if p.startswith("edit_")],
                "🗑️ Удаление": [p for p in all_permissions if p.startswith("delete_")],
                "️ Администрирование": [p for p in all_permissions if p in [
                    "export_reports", "backup_database", "manage_settings",
                    "change_password", "view_all_users_passwords"
                ]]
            }

            for category_name, perms in categories.items():
                cat_label = QLabel(category_name)
                cat_label.setStyleSheet("font-weight: bold; font-size: 13px; margin-top: 8px;")
                permissions_layout.addWidget(cat_label)

                grid = QGridLayout()
                grid.setSpacing(5)
                for i, perm in enumerate(perms):
                    cb = QCheckBox(perm)
                    cb.setToolTip(perm)
                    self.permission_checks[perm] = cb
                    grid.addWidget(cb, i // 3, i % 3)
                permissions_layout.addLayout(grid)

            quick_btn_layout = QHBoxLayout()
            select_all_btn = QPushButton("Выбрать все")
            select_all_btn.setMinimumHeight(35)
            select_all_btn.clicked.connect(self.select_all_permissions)
            deselect_all_btn = QPushButton("Снять все")
            deselect_all_btn.setMinimumHeight(35)
            deselect_all_btn.clicked.connect(self.deselect_all_permissions)
            quick_btn_layout.addWidget(select_all_btn)
            quick_btn_layout.addWidget(deselect_all_btn)
            quick_btn_layout.addStretch()
            permissions_layout.addLayout(quick_btn_layout)

        content_layout.addWidget(permissions_group)
        content_layout.addStretch()

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # === Кнопки управления ===
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.save_user)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

        if self.is_edit_mode:
            self.load_user_data()

    def toggle_password_visibility(self):
        """Переключение видимости пароля."""
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁️")

    def toggle_confirm_visibility(self):
        """Переключение видимости подтверждения пароля."""
        if self.confirm_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_confirm_btn.setText("🙈")
        else:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_confirm_btn.setText("👁️")

    def load_user_data(self):
        """Загрузка данных пользователя в форму."""
        if not hasattr(self, 'username_input'):
            return

        self.username_input.setText(self.user.username)
        self.fullname_input.setText(self.user.full_name)
        self.email_input.setText(self.user.email or "")
        self.active_check.setChecked(bool(self.user.is_active))

        if self.user.username == "superadmin":
            self.role_combo.setCurrentIndex(0)
        else:
            role_map = {
                UserRole.ADMIN: 1 if self.current_admin and self.current_admin.username == "superadmin" else 0,
                UserRole.MANAGER: 2 if self.current_admin and self.current_admin.username == "superadmin" else 1,
                UserRole.OPERATOR: 3 if self.current_admin and self.current_admin.username == "superadmin" else 2
            }
            self.role_combo.setCurrentIndex(role_map.get(self.user.role, 2))

        if not self.is_superadmin_edit and hasattr(self, 'permission_checks'):
            custom_perms = self.user.get_custom_permissions()

            if not custom_perms:
                role_perms = self.user._get_role_permissions()
                for perm, cb in self.permission_checks.items():
                    cb.setChecked(perm in role_perms)
            else:
                for perm, cb in self.permission_checks.items():
                    cb.setChecked(perm in custom_perms)

        # Загрузка паспортных данных
        if hasattr(self, 'passport_series_input') and not self.is_superadmin_edit:
            from models.client import Client

            # Ищем клиента по email или ФИО
            client = None
            if self.user.email:
                client = self.db.query(Client).filter(Client.email == self.user.email).first()

            if not client:
                client = self.db.query(Client).filter(Client.full_name == self.user.full_name).first()

            if client:
                try:
                    if hasattr(client, 'passport_series'):
                        self.passport_series_input.setText(client.passport_series or "")
                    if hasattr(client, 'passport_number'):
                        self.passport_number_input.setText(client.passport_number or "")
                    if hasattr(client, 'passport_issue_place'):
                        self.passport_issue_place_input.setText(client.passport_issue_place or "")

                    # Дата выдачи (безопасная загрузка)
                    if hasattr(client, 'passport_issue_date') and client.passport_issue_date:
                        try:
                            self.passport_issue_date_input.setText(
                                client.passport_issue_date.strftime("%d.%m.%Y")
                            )
                        except:
                            pass

                    print(f"✅ Паспортные данные загружены для клиента ID {client.id}")
                except Exception as e:
                    print(f"⚠️ Ошибка загрузки паспортных данных: {e}")

    def select_all_permissions(self):
        """Выбрать все права."""
        for cb in self.permission_checks.values():
            cb.setChecked(True)

    def deselect_all_permissions(self):
        """Снять все права."""
        for cb in self.permission_checks.values():
            cb.setChecked(False)

    def save_user(self):
        """Сохранение/создание пользователя."""
        # === ПОДРОБНОЕ ЛОГИРОВАНИЕ ===
        logger.info("=" * 60)
        logger.info("НАЧАЛО СОХРАНЕНИЯ ПОЛЬЗОВАТЕЛЯ")
        logger.info(f"Режим: {'РЕДАКТИРОВАНИЕ' if self.is_edit_mode else 'СОЗДАНИЕ'}")
        if self.is_edit_mode:
            logger.info(f"ID пользователя: {self.user.id}")
            logger.info(f"Текущий логин: {self.user.username}")
        logger.info("=" * 60)

        username = self.username_input.text().strip()
        fullname = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_password_input.text()
        is_active = self.active_check.isChecked()

        logger.info(f"Введенный логин: '{username}'")
        logger.info(f"Введенное ФИО: '{fullname}'")
        logger.info(f"Введенный пароль: '{'***' if password else 'ПУСТО'}' (длина: {len(password)})")
        logger.info(f"Пароли совпадают: {password == confirm}")

        # Валидация
        if not username or not fullname:
            QMessageBox.warning(self, "Ошибка", "Логин и ФИО обязательны")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Ошибка", "Логин должен содержать минимум 3 символа")
            return

        if not self.is_edit_mode:
            if not password:
                QMessageBox.warning(self, "Ошибка", "Пароль обязателен при создании пользователя")
                return
        else:
            if password and password != confirm:
                QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
                return
            if password and len(password) < 6:
                QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6 символов")
                return

        # Определяем роль
        role_index = self.role_combo.currentIndex()
        logger.info(f"Выбранный индекс роли: {role_index}")

        if self.current_admin and self.current_admin.username == "superadmin":
            role_map = {
                0: UserRole.SUPER_ADMIN,
                1: UserRole.ADMIN,
                2: UserRole.MANAGER,
                3: UserRole.OPERATOR,
                4: UserRole.USER
            }
            is_superadmin = (role_index == 0)
        else:
            role_map = {
                0: UserRole.ADMIN,
                1: UserRole.MANAGER,
                2: UserRole.OPERATOR,
                3: UserRole.USER
            }
            is_superadmin = False

        role = role_map.get(role_index, UserRole.OPERATOR)
        logger.info(f"Выбранная роль: {role.value}")

        if self.is_edit_mode:
            if self.user.username == "superadmin" and self.current_admin.username != "superadmin":
                QMessageBox.critical(self, "Ошибка", "Только Главный Администратор может редактировать себя")
                return

            if not is_superadmin and self.user.id == self.current_admin.id:
                role = self.user.role

            if self.user.username == "superadmin":
                role = UserRole.SUPER_ADMIN

        selected_perms = []
        if not is_superadmin and hasattr(self, 'permission_checks'):
            selected_perms = [perm for perm, cb in self.permission_checks.items() if cb.isChecked()]

            if self.is_edit_mode:
                data = {
                    "username": username,
                    "full_name": fullname,
                    "email": email if email else None,
                    "role": role.value,
                    "is_active": is_active,
                }

                if password:
                    data["password"] = password

                if selected_perms:
                    data["custom_permissions"] = selected_perms
                elif not is_superadmin:
                    data["custom_permissions"] = []

                result = self.auth_service.update_user(self.user.id, data, self.current_admin)

                # Сохраняем паспортные данные клиента
                if result["success"]:
                    try:
                        from models.client import Client
                        from datetime import datetime

                        # Ищем клиента по email или ФИО
                        client = None
                        if email:
                            client = self.db.query(Client).filter(Client.email == email).first()

                        if not client:
                            client = self.db.query(Client).filter(Client.full_name == fullname).first()

                        if not client:
                            # Создаем нового клиента
                            client = Client(
                                full_name=fullname,
                                passport_series=self.passport_series_input.text().strip() if hasattr(self,
                                                                                                     'passport_series_input') else "",
                                passport_number=self.passport_number_input.text().strip() if hasattr(self,
                                                                                                     'passport_number_input') else "",
                                phone="",
                                email=email,
                                passport_issue_date=None,
                                passport_issue_place=""
                            )
                            self.db.add(client)
                            print(f"✅ Создан новый клиент: {fullname}")
                        else:
                            if hasattr(self, 'passport_series_input'):
                                client.passport_series = self.passport_series_input.text().strip()
                            if hasattr(self, 'passport_number_input'):
                                client.passport_number = self.passport_number_input.text().strip()
                            if hasattr(self, 'passport_issue_place_input'):
                                client.passport_issue_place = self.passport_issue_place_input.text().strip()

                            # Дата выдачи (с безопасной проверкой)
                            if hasattr(self, 'passport_issue_date_input'):
                                date_text = self.passport_issue_date_input.text().strip()
                                if date_text:
                                    try:
                                        client.passport_issue_date = datetime.strptime(date_text, "%d.%m.%Y").date()
                                    except Exception as e:
                                        print(f"⚠️ Неверный формат даты: {date_text} - {e}")

                            print(f"✅ Обновлен клиент ID {client.id}: {fullname}")

                        self.db.commit()
                        print("✅ Паспортные данные сохранены в БД")
                    except Exception as e:
                        print(f"⚠️ Ошибка сохранения паспортных данных: {e}")
                        import traceback
                        traceback.print_exc()
            else:
                result = self.auth_service.create_user(
                    username=username,
                    password=password,
                    full_name=fullname,
                    email=email if email else None,
                    role=role,
                    created_by=self.current_admin,
                    custom_permissions=selected_perms if selected_perms else None
                )

            if result["success"]:
                QMessageBox.information(
                    self, "Успех",
                    "Пользователь успешно обновлён!" if self.is_edit_mode else "Пользователь успешно создан!"
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)
