from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
                             QPushButton, QComboBox, QCheckBox, QSpinBox, QFileDialog,
                             QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt
import os
import json


class SettingsWidget(QWidget):
    """Виджет настроек приложения."""

    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_user = current_user  # Получаем пользователя из параметра
        self.settings_file = "settings.json"
        self.settings = self.load_settings()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        header_label = QLabel("⚙️ Настройки приложения")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # ПРОВЕРКА ПРАВ: управление настройками
        if self.current_user and not self.current_user.has_permission('manage_settings'):
            no_access_label = QLabel(
                "⛔ У вас нет прав для изменения настроек приложения.\n"
                "Обратитесь к администратору системы."
            )
            no_access_label.setObjectName("no_access_label")
            no_access_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_access_label.setStyleSheet("font-size: 16px; color: #64748B; padding: 40px;")
            layout.addWidget(no_access_label)

            # Показываем только информацию о приложении (без возможности менять)
            about_group = QGroupBox("ℹ️ О приложении")
            about_layout = QVBoxLayout(about_group)
            about_text = QLabel(
                "AutoRent Pro v1.0.0\n"
                "Информационная система управления арендой автомобилей\n"
                "Разработано в рамках учебной практики МТУСИ\n"
                "Кафедра «Программная инженерия»\n"
                "2026 год"
            )
            about_text.setWordWrap(True)
            about_layout.addWidget(about_text)

            self.github_btn = QPushButton("📂 Открыть репозиторий GitHub")
            self.github_btn.setMinimumHeight(45)
            self.github_btn.clicked.connect(lambda: self.open_url("https://github.com/Xynary25/MTUCI-Car-Rental"))
            about_layout.addWidget(self.github_btn)

            self.support_btn = QPushButton("✉️ Связаться с поддержкой")
            self.support_btn.setMinimumHeight(45)
            self.support_btn.clicked.connect(lambda: self.open_url("mailto:bogdan.coolline25@gmail.com"))
            about_layout.addWidget(self.support_btn)

            layout.addWidget(about_group)
            layout.addStretch()
            return

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # Группа: Внешний вид (заменена на подсказку)
        appearance_group = QGroupBox("🎨 Внешний вид")
        appearance_layout = QVBoxLayout(appearance_group)

        theme_hint = QLabel(
            "💡 Тема оформления переключается кнопкой в левой панели,\n"
            "рядом с информацией о пользователе.\n\n"
            " Тёмная тема / ☀️ Светлая тема"
        )
        theme_hint.setWordWrap(True)
        theme_hint.setObjectName("hint_label")
        appearance_layout.addWidget(theme_hint)

        # Оставляем только размер шрифта
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Размер шрифта:")
        font_size_label.setStyleSheet("font-weight: bold;")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 20)
        self.font_size_spin.setValue(self.settings.get("font_size", 13))
        self.font_size_spin.setMinimumHeight(40)
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_spin)
        font_size_layout.addStretch()
        appearance_layout.addLayout(font_size_layout)

        content_layout.addWidget(appearance_group)

        # Группа: База данных
        database_group = QGroupBox("💾 База данных")
        database_layout = QVBoxLayout(database_group)

        db_type_layout = QHBoxLayout()
        db_type_label = QLabel("Тип базы данных:")
        db_type_label.setStyleSheet("font-weight: bold;")
        self.db_type_combo = QComboBox()
        self.db_type_combo.setMinimumHeight(40)
        self.db_type_combo.addItems(["SQLite (локальная)", "PostgreSQL (сервер)"])
        current_db = self.settings.get("db_type", "sqlite")
        self.db_type_combo.setCurrentIndex(0 if current_db == "sqlite" else 1)
        db_type_layout.addWidget(db_type_label)
        db_type_layout.addWidget(self.db_type_combo)
        db_type_layout.addStretch()
        database_layout.addLayout(db_type_layout)

        backup_layout = QHBoxLayout()
        backup_label = QLabel("Папка для резервных копий:")
        backup_label.setStyleSheet("font-weight: bold;")
        self.backup_path_label = QLabel(self.settings.get("backup_path", "./backups"))
        self.backup_path_label.setStyleSheet("color: #64748B; padding: 5px;")
        self.backup_btn = QPushButton("📁 Выбрать папку")
        self.backup_btn.setMinimumHeight(40)
        self.backup_btn.clicked.connect(self.select_backup_path)
        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(self.backup_path_label)
        backup_layout.addWidget(self.backup_btn)
        database_layout.addLayout(backup_layout)

        content_layout.addWidget(database_group)

        # Группа: Автоматическое резервное копирование
        auto_backup_group = QGroupBox("🔄 Автоматическое резервное копирование")
        auto_backup_layout = QVBoxLayout(auto_backup_group)

        # Включение/выключение автобэкапа
        self.auto_backup_check = QCheckBox("Включить автоматическое резервное копирование")
        self.auto_backup_check.setChecked(self.settings.get("auto_backup", True))
        self.auto_backup_check.toggled.connect(self.on_auto_backup_toggled)
        auto_backup_layout.addWidget(self.auto_backup_check)

        # Частота бэкапов
        frequency_layout = QHBoxLayout()
        frequency_label = QLabel("Частота:")
        self.frequency_combo = QComboBox()
        self.frequency_combo.setMinimumHeight(40)
        self.frequency_combo.addItems(
            ["Ежечасно", "Ежедневно", "Еженедельно", "Ежемесячно", "⚡ Тестовый режим (через 1 мин)"])
        frequency_map = {"hourly": 0, "daily": 1, "weekly": 2, "monthly": 3, "test": 4}
        current_freq = self.settings.get("auto_backup_frequency", "daily")
        self.frequency_combo.setCurrentIndex(frequency_map.get(current_freq, 1))
        self.frequency_combo.currentIndexChanged.connect(self.on_frequency_changed)
        frequency_layout.addWidget(frequency_label)
        frequency_layout.addWidget(self.frequency_combo)
        frequency_layout.addStretch()
        auto_backup_layout.addLayout(frequency_layout)

        # Время выполнения
        time_layout = QHBoxLayout()
        time_label = QLabel("Время выполнения:")
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setValue(self.settings.get("auto_backup_hour", 23))
        self.hour_spin.setMinimumHeight(40)
        self.hour_spin.setSuffix(" ч")

        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setValue(self.settings.get("auto_backup_minute", 0))
        self.minute_spin.setMinimumHeight(40)
        self.minute_spin.setSuffix(" мин")

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(self.minute_spin)
        time_layout.addStretch()
        auto_backup_layout.addLayout(time_layout)

        # День недели (для еженедельного бэкапа)
        self.day_widget = QWidget()
        day_layout = QHBoxLayout(self.day_widget)
        day_layout.setContentsMargins(0, 0, 0, 0)
        day_label = QLabel("День недели:")
        self.day_combo = QComboBox()
        self.day_combo.setMinimumHeight(40)
        self.day_combo.addItems(["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"])
        self.day_combo.setCurrentIndex(self.settings.get("auto_backup_day", 0))
        day_layout.addWidget(day_label)
        day_layout.addWidget(self.day_combo)
        day_layout.addStretch()
        auto_backup_layout.addWidget(self.day_widget)
        self.day_widget.setVisible(False)

        # Максимальное количество бэкапов
        max_backups_layout = QHBoxLayout()
        max_backups_label = QLabel("Макс. количество бэкапов:")
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(0, 100)
        self.max_backups_spin.setValue(self.settings.get("max_backups", 10))
        self.max_backups_spin.setMinimumHeight(40)
        self.max_backups_spin.setSpecialValueText("Без ограничений")
        max_backups_layout.addWidget(max_backups_label)
        max_backups_layout.addWidget(self.max_backups_spin)
        max_backups_layout.addStretch()
        auto_backup_layout.addLayout(max_backups_layout)

        # Статус планировщика
        self.status_label = QLabel("Статус: Не запущен")
        self.status_label.setWordWrap(True)
        auto_backup_layout.addWidget(self.status_label)

        # КНОПКА РУЧНОЙ ПРОВЕРКИ
        self.test_backup_btn = QPushButton("🧪 Создать резервную копию сейчас")
        self.test_backup_btn.setMinimumHeight(45)
        self.test_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        self.test_backup_btn.clicked.connect(self.run_manual_backup)
        auto_backup_layout.addWidget(self.test_backup_btn)

        self.update_scheduler_ui()
        content_layout.addWidget(auto_backup_group)

        # Группа: Уведомления
        notifications_group = QGroupBox("🔔 Уведомления")
        notifications_layout = QVBoxLayout(notifications_group)

        self.email_notifications_check = QCheckBox("Email-уведомления о критических событиях")
        self.email_notifications_check.setChecked(self.settings.get("email_notifications", False))
        notifications_layout.addWidget(self.email_notifications_check)

        content_layout.addWidget(notifications_group)

        # Группа: О приложении
        about_group = QGroupBox("ℹ️ О приложении")
        about_layout = QVBoxLayout(about_group)

        about_text = QLabel(
            "AutoRent Pro v1.0.0\n"
            "Информационная система управления арендой автомобилей\n"
            "Разработано в рамках учебной практики МТУСИ\n"
            "Кафедра «Программная инженерия»\n"
            "2026 год"
        )
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)

        self.github_btn = QPushButton("📂 Открыть репозиторий GitHub")
        self.github_btn.setMinimumHeight(45)
        self.github_btn.clicked.connect(lambda: self.open_url("https://github.com/Xynary25/MTUCI-Car-Rental"))
        about_layout.addWidget(self.github_btn)

        self.support_btn = QPushButton("✉️ Связаться с поддержкой")
        self.support_btn.setMinimumHeight(45)
        self.support_btn.clicked.connect(lambda: self.open_url("mailto:bogdan.coolline25@gmail.com"))
        about_layout.addWidget(self.support_btn)

        content_layout.addWidget(about_group)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить настройки")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.save_settings)
        self.reset_btn = QPushButton("🔄 Сбросить по умолчанию")
        self.reset_btn.setMinimumHeight(45)
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.reset_btn)
        content_layout.addLayout(buttons_layout)

        content_layout.addStretch()

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

    def run_manual_backup(self):
        """Ручной запуск резервного копирования для проверки."""
        self.test_backup_btn.setEnabled(False)
        self.test_backup_btn.setText("⏳ Создание резервной копии...")

        from utils.backup_scheduler import backup_scheduler

        # Используем папку из настроек
        backup_dir = self.backup_path_label.text()
        backup_scheduler.backup_dir = backup_dir

        result = backup_scheduler.run_backup_now()

        self.test_backup_btn.setEnabled(True)
        self.test_backup_btn.setText("🧪 Создать резервную копию сейчас")

        if result["success"]:
            QMessageBox.information(
                self, "✅ Успех",
                f"Резервная копия успешно создана!\n\n"
                f"Путь: {result['path']}\n\n"
                f"Проверьте папку {backup_dir}"
            )
            # Обновляем статус
            self.update_scheduler_ui()
        else:
            QMessageBox.critical(
                self, "❌ Ошибка",
                f"Не удалось создать резервную копию:\n\n{result['error']}"
            )

    def load_settings(self) -> dict:
        """Загрузка настроек из файла."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "theme": "light",
            "font_size": 13,
            "db_type": "sqlite",
            "backup_path": "./backups",
            "auto_backup": True,
            "auto_backup_frequency": "daily",
            "auto_backup_hour": 23,
            "auto_backup_minute": 0,
            "auto_backup_day": 0,
            "max_backups": 10,
            "email_notifications": False
        }

    def save_settings(self):
        """Сохранение настроек в файл."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('manage_settings'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для изменения настроек")
            return

        frequency_map = {0: "hourly", 1: "daily", 2: "weekly", 3: "monthly", 4: "test"}

        self.settings["font_size"] = self.font_size_spin.value()
        self.settings["db_type"] = "sqlite" if self.db_type_combo.currentIndex() == 0 else "postgresql"
        self.settings["backup_path"] = self.backup_path_label.text()
        self.settings["auto_backup"] = self.auto_backup_check.isChecked()
        self.settings["auto_backup_frequency"] = frequency_map.get(self.frequency_combo.currentIndex(), "daily")
        self.settings["auto_backup_hour"] = self.hour_spin.value()
        self.settings["auto_backup_minute"] = self.minute_spin.value()
        self.settings["auto_backup_day"] = self.day_combo.currentIndex()
        self.settings["max_backups"] = self.max_backups_spin.value()
        self.settings["email_notifications"] = self.email_notifications_check.isChecked()

        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)

            # Перезапуск планировщика с новыми настройками
            if self.parent_window and hasattr(self.parent_window, 'restart_backup_scheduler'):
                self.parent_window.restart_backup_scheduler(self.settings)

            QMessageBox.information(self, "Успех", "Настройки успешно сохранены!")
            self.update_scheduler_ui()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки:\n{str(e)}")

    def reset_settings(self):
        """Сброс настроек к значениям по умолчанию."""
        # Дополнительная проверка прав
        if self.current_user and not self.current_user.has_permission('manage_settings'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для сброса настроек")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Сбросить все настройки к значениям по умолчанию?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings = {
                "theme": "light",
                "font_size": 13,
                "db_type": "sqlite",
                "backup_path": "./backups",
                "auto_backup": True,
                "auto_backup_frequency": "daily",
                "auto_backup_hour": 23,
                "auto_backup_minute": 0,
                "auto_backup_day": 0,
                "max_backups": 10,
                "email_notifications": False
            }
            self.font_size_spin.setValue(13)
            self.db_type_combo.setCurrentIndex(0)
            self.backup_path_label.setText("./backups")
            self.auto_backup_check.setChecked(True)
            self.frequency_combo.setCurrentIndex(1)
            self.hour_spin.setValue(23)
            self.minute_spin.setValue(0)
            self.day_combo.setCurrentIndex(0)
            self.max_backups_spin.setValue(10)
            self.email_notifications_check.setChecked(False)

            self.update_scheduler_ui()
            QMessageBox.information(self, "Успех", "Настройки сброшены!")

    def on_font_size_changed(self, size):
        """Обработка изменения размера шрифта."""
        if self.parent_window and hasattr(self.parent_window, 'apply_font_size'):
            self.parent_window.apply_font_size(size)

    def on_auto_backup_toggled(self, checked: bool):
        """Обработка переключения автобэкапа."""
        self.update_scheduler_ui()

    def on_frequency_changed(self, index: int):
        """Обработка изменения частоты бэкапов."""
        if not self.auto_backup_check.isChecked():
            return

        # Показывать/скрывать выбор дня недели
        if index == 2:  # Еженедельно
            self.day_widget.setVisible(True)
        else:
            self.day_widget.setVisible(False)

    def update_scheduler_ui(self):
        """Обновление UI в зависимости от состояния автобэкапа."""
        enabled = self.auto_backup_check.isChecked()
        self.frequency_combo.setEnabled(enabled)
        self.hour_spin.setEnabled(enabled)
        self.minute_spin.setEnabled(enabled)
        self.max_backups_spin.setEnabled(enabled)

        # Показываем/скрываем день недели (только для еженедельного бэкапа)
        if enabled:
            freq_index = self.frequency_combo.currentIndex()
            if freq_index == 2:  # Еженедельно
                self.day_widget.setVisible(True)
            else:
                self.day_widget.setVisible(False)
        else:
            self.day_widget.setVisible(False)

        # Обновление статуса
        from utils.backup_scheduler import backup_scheduler
        status = backup_scheduler.get_status()
        if status["running"]:
            self.status_label.setText(f"✅ Статус: Активен\nСледующий бэкап: {status['next_run']}\n{status['job_name']}")
        else:
            self.status_label.setText("⚠️ Статус: Остановлен")

    def select_backup_path(self):
        """Выбор папки для резервных копий."""
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку для резервных копий"
        )
        if path:
            self.backup_path_label.setText(path)

    def open_url(self, url):
        """Открытие URL в браузере."""
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(url))