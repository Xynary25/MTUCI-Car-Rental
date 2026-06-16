from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QMessageBox, QHeaderView, QAbstractItemView, QLabel,
                             QLineEdit, QDialog)
from PyQt6.QtCore import Qt
from database import SessionLocal
from utils.auth_service import AuthService
from models.user import User
from views.user_edit_dialog import UserEditDialog


class UsersWidget(QWidget):
    """Виджет управления пользователями системы."""

    def __init__(self, current_user: User = None):
        super().__init__()
        self.current_user = current_user
        self.db = SessionLocal()
        self.auth_service = AuthService(self.db)
        self.all_users = []

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок раздела
        header_label = QLabel("👥 Управление пользователями")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # Проверка прав доступа
        if not current_user or not current_user.has_permission('view_users'):
            no_access_label = QLabel(
                "⛔ У вас нет прав для просмотра этого раздела.\n"
                "Обратитесь к администратору системы."
            )
            no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_access_label.setStyleSheet("font-size: 16px; color: #64748B; padding: 40px;")
            layout.addWidget(no_access_label)
            layout.addStretch()
            return

        # Панель поиска
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Поиск по логину или ФИО...")
        self.search_input.textChanged.connect(self.filter_users)
        self.search_input.setMaximumWidth(400)
        self.search_input.setMinimumHeight(40)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # Панель инструментов
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить пользователя")
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_user)

        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setMinimumHeight(45)
        self.edit_btn.clicked.connect(self.edit_user)

        self.deactivate_btn = QPushButton("🚫 Деактивировать")
        self.deactivate_btn.setMinimumHeight(45)
        self.deactivate_btn.clicked.connect(self.deactivate_user)

        self.activate_btn = QPushButton("✅ Активировать")
        self.activate_btn.setMinimumHeight(45)
        self.activate_btn.clicked.connect(self.activate_user)
        self.activate_btn.setEnabled(False)  # Изначально неактивна

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setMinimumHeight(45)
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.delete_user)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_data)

        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.deactivate_btn)
        toolbar.addWidget(self.activate_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_btn)
        layout.addLayout(toolbar)

        # Подсказка
        hint_label = QLabel(
            "💡 Двойной клик по пользователю для редактирования. "
            "Деактивация запрещает вход без удаления данных."
        )
        hint_label.setObjectName("hint_label")
        layout.addWidget(hint_label)

        # Таблица пользователей — СОЗДАЁТСЯ ЗДЕСЬ
        self.table = QTableWidget()
        self.table.setObjectName("users_table")
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Логин", "ФИО", "Email", "Роль",
            "Статус", "Последний вход", "Создан"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.edit_user)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        # ИСПРАВЛЕНИЕ: Подключаем сигнал ПОСЛЕ создания таблицы
        self.table.itemSelectionChanged.connect(self.update_button_states)

        # Информация о текущем пользователе
        info_label = QLabel(
            f"🔑 Вы вошли как: {current_user.full_name} ({current_user.role.value})"
        )
        info_label.setStyleSheet("font-size: 12px; color: #64748B; padding: 5px;")
        layout.addWidget(info_label)

        self.load_data()

    def load_data(self):
        """Загрузка списка пользователей."""
        try:
            # Принудительно обновляем объекты из БД (ВАЖНО!)
            if hasattr(self, 'db') and self.db:
                self.db.expire_all()

            self.all_users = self.auth_service.get_all_users()
            self.table.setRowCount(len(self.all_users))

            for row, user in enumerate(self.all_users):
                # ID
                item_id = QTableWidgetItem(str(user.id))
                item_id.setFlags(item_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, item_id)

                # Логин
                item_username = QTableWidgetItem(user.username)
                item_username.setFlags(item_username.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, item_username)

                # ФИО
                item_fullname = QTableWidgetItem(user.full_name)
                item_fullname.setFlags(item_fullname.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, item_fullname)

                # Email
                item_email = QTableWidgetItem(user.email or "")
                item_email.setFlags(item_email.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 3, item_email)

                # Роль
                item_role = QTableWidgetItem(user.role.value)
                item_role.setFlags(item_role.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 4, item_role)

                # Статус (БЕЗ зачеркивания)
                status_item = QTableWidgetItem("✅ Активен" if user.is_active else "❌ Отключен")
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # НЕ применяем setStrikeOut - это вызывает зачеркивание!
                self.table.setItem(row, 5, status_item)

                # Последний вход
                item_last_login = QTableWidgetItem(
                    user.last_login.strftime("%d.%m.%Y %H:%M") if user.last_login else "Никогда"
                )
                item_last_login.setFlags(item_last_login.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 6, item_last_login)

                # Хеш пароля (первые 16 символов)
                item_password = QTableWidgetItem(
                    user.password_hash[:16] + "..." if user.password_hash else ""
                )
                item_password.setFlags(item_password.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 7, item_password)

            # Применяем авто-размер строк
            from utils.table_utils import auto_resize_table_rows
            auto_resize_table_rows(self.table, min_height=40)

        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные:\n{str(e)}")

    def display_users(self, users):
        """Отображение пользователей в таблице."""
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username))
            self.table.setItem(row, 2, QTableWidgetItem(user.full_name))
            self.table.setItem(row, 3, QTableWidgetItem(user.email or "—"))

            # Роль с цветовой индикацией
            role_item = QTableWidgetItem(user.role.value)
            if user.role.value == "admin":
                role_item.setForeground(Qt.GlobalColor.darkRed)
            elif user.role.value == "manager":
                role_item.setForeground(Qt.GlobalColor.darkBlue)
            else:
                role_item.setForeground(Qt.GlobalColor.darkGreen)
            self.table.setItem(row, 4, role_item)

            # Статус
            status_item = QTableWidgetItem("✅ Активен" if user.is_active else "🚫 Деактивирован")
            if user.is_active:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, status_item)

            self.table.setItem(row, 6, QTableWidgetItem(
                user.last_login.strftime("%d.%m.%Y %H:%M") if user.last_login else "Никогда"
            ))
            self.table.setItem(row, 7, QTableWidgetItem(
                user.created_at.strftime("%d.%m.%Y %H:%M") if user.created_at else "—"
            ))

        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.table, min_height=40)

    def filter_users(self, search_text):
        """Фильтрация пользователей по логину или ФИО."""
        search_text = search_text.lower().strip()
        if not search_text:
            self.display_users(self.all_users)
            return

        filtered = [
            user for user in self.all_users
            if search_text in user.username.lower() or search_text in user.full_name.lower()
        ]
        self.display_users(filtered)

    def add_user(self):
        """Создание нового пользователя."""
        dialog = UserEditDialog(user=None, current_admin=self.current_user, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.load_data()

    def edit_user(self):
        """Редактирование выбранного пользователя."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для редактирования")
            return

        row = selected[0].row()
        user_id = int(self.table.item(row, 0).text())

        # Получаем объект пользователя из БД
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
            return

        dialog = UserEditDialog(user=user, current_admin=self.current_user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # ✅ ИСПРАВЛЕНИЕ: обновляем данные после успешного сохранения
            self.load_data()
            QMessageBox.information(self, "Успех", "Данные обновлены")

    def update_button_states(self):
        """Обновление состояния кнопок в зависимости от выбранного пользователя."""
        selected = self.table.selectedItems()
        if not selected:
            self.deactivate_btn.setEnabled(False)
            self.activate_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        row = selected[0].row()
        user_id = int(self.table.item(row, 0).text())
        user = next((u for u in self.all_users if u.id == user_id), None)

        if not user:
            self.deactivate_btn.setEnabled(False)
            self.activate_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        # SuperAdmin нельзя редактировать/удалять
        if user.username == "superadmin":
            self.deactivate_btn.setEnabled(False)
            self.activate_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        # Нельзя редактировать/удалять самого себя
        if user.id == self.current_user.id:
            self.deactivate_btn.setEnabled(False)
            self.activate_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        # ИСПРАВЛЕНИЕ: Активируем кнопки в зависимости от статуса
        self.deactivate_btn.setEnabled(user.is_active)  # Деактивировать можно только активного
        self.activate_btn.setEnabled(not user.is_active)  # Активировать можно только неактивного
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def deactivate_user(self):
        """Деактивация пользователя."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя")
            return

        row = selected[0].row()
        user_id = int(self.table.item(row, 0).text())
        user = next((u for u in self.all_users if u.id == user_id), None)

        if not user or not user.is_active:
            QMessageBox.warning(self, "Внимание", "Выберите активного пользователя")
            return

        # Проверка на Главного Администратора
        if user.username == "superadmin":
            QMessageBox.critical(self, "Ошибка", "Нельзя деактивировать Главного Администратора")
            return

        if user.id == self.current_user.id:
            QMessageBox.warning(self, "Ошибка", "Нельзя деактивировать самого себя")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите деактивировать пользователя {user.username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = self.auth_service.update_user(
                user_id,
                {"is_active": False},
                self.current_user
            )
            if result["success"]:
                QMessageBox.information(self, "Успех", "Пользователь деактивирован")
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def activate_user(self):
        """Активация пользователя."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя")
            return

        row = selected[0].row()
        user_id = int(self.table.item(row, 0).text())
        user = next((u for u in self.all_users if u.id == user_id), None)

        if not user or user.is_active:
            QMessageBox.warning(self, "Внимание", "Выберите деактивированного пользователя")
            return

        # Проверка на Главного Администратора
        if user.username == "superadmin":
            QMessageBox.critical(self, "Ошибка", "Нельзя изменить статус Главного Администратора")
            return

        if user.id == self.current_user.id:
            QMessageBox.warning(self, "Ошибка", "Нельзя активировать самого себя")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите активировать пользователя {user.username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = self.auth_service.update_user(
                user_id,
                {"is_active": True},
                self.current_user
            )
            if result["success"]:
                QMessageBox.information(self, "Успех", "Пользователь активирован")
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def delete_user(self):
        """Удаление пользователя."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя")
            return

        row = selected[0].row()
        user_id = int(self.table.item(row, 0).text())
        user = next((u for u in self.all_users if u.id == user_id), None)

        if not user:
            return

        if user.id == self.current_user.id:
            QMessageBox.warning(self, "Ошибка", "Нельзя удалить самого себя")
            return

        reply = QMessageBox.warning(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите УДАЛИТЬ пользователя {user.username}?\n\n"
            f"Это действие необратимо!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = self.auth_service.delete_user(user_id, self.current_user)
            if result["success"]:
                QMessageBox.information(self, "Успех", f"Пользователь {user.username} удалён")
                self.load_data()
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def closeEvent(self, event):
        """Закрытие виджета пользователей."""
        if hasattr(self, 'db'):
            self.db.close()
            print("Сессия БД пользователей закрыта")
        super().closeEvent(event)