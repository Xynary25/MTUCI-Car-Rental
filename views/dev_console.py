from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QComboBox, QGroupBox, QScrollArea,
                             QFrame, QSplitter, QTabWidget, QWidget, QTreeWidget,
                             QTreeWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QFont, QColor
from database import SessionLocal
import logging
import os
from pathlib import Path
from datetime import datetime, timedelta


class DevConsoleDialog(QDialog):
    """Расширенная консоль разработчика с полным логированием."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔧 Консоль разработчика - DriveControl")
        self.resize(1200, 800)

        self.db = SessionLocal()
        self.current_filter = "ALL"
        self.init_ui()
        self.load_logs()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_logs)
        self.refresh_timer.start(3000)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("🔍 Система мониторинга и логирования")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e293b;")
        layout.addWidget(title)

        # Панель управления
        control_layout = QHBoxLayout()

        # Фильтр уровня логов
        control_layout.addWidget(QLabel("📊 Уровень:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self.on_filter_changed)
        control_layout.addWidget(self.level_filter)

        # Фильтр по модулю
        control_layout.addWidget(QLabel("📁 Модуль:"))
        self.module_filter = QComboBox()
        self.module_filter.addItems(["ALL", "WEB", "DESKTOP", "AUTH", "DB", "SUPPORT", "ALL"])
        control_layout.addWidget(self.module_filter)

        # Кнопки
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(35)
        self.refresh_btn.clicked.connect(self.load_logs)
        control_layout.addWidget(self.refresh_btn)

        self.clear_btn = QPushButton("🗑️ Очистить")
        self.clear_btn.setMinimumHeight(35)
        self.clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(self.clear_btn)

        self.export_btn = QPushButton("💾 Экспорт")
        self.export_btn.setMinimumHeight(35)
        self.export_btn.clicked.connect(self.export_logs)
        control_layout.addWidget(self.export_btn)

        layout.addLayout(control_layout)

        # Вкладки
        tabs = QTabWidget()

        # Вкладка 1: Логи веб-портала
        web_logs_tab = self.create_web_logs_tab()
        tabs.addTab(web_logs_tab, "🌐 Веб-портал")

        # Вкладка 2: Логи СУ
        desktop_logs_tab = self.create_desktop_logs_tab()
        tabs.addTab(desktop_logs_tab, "💻 СУ (Desktop)")

        # Вкладка 3: Активные пользователи
        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "👥 Пользователи")

        # Вкладка 4: Статистика БД
        db_tab = self.create_database_tab()
        tabs.addTab(db_tab, "🗄️ База данных")

        # Вкладка 5: Системная информация
        system_tab = self.create_system_tab()
        tabs.addTab(system_tab, "⚙️ Система")

        layout.addWidget(tabs)

        # Кнопка закрытия
        close_btn = QPushButton("❌ Закрыть")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def create_web_logs_tab(self):
        """Вкладка логов веб-портала."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Область логов
        self.web_logs = QTextEdit()
        self.web_logs.setReadOnly(True)
        self.web_logs.setFont(QFont("Courier New", 10))
        self.web_logs.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.web_logs)

        return widget

    def create_desktop_logs_tab(self):
        """Вкладка логов СУ."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Область логов
        self.desktop_logs = QTextEdit()
        self.desktop_logs.setReadOnly(True)
        self.desktop_logs.setFont(QFont("Courier New", 10))
        self.desktop_logs.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.desktop_logs)

        return widget

    def create_users_tab(self):
        """Вкладка активных пользователей."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Дерево пользователей
        self.users_tree = QTreeWidget()
        self.users_tree.setHeaderLabels(["Пользователь", "Роль", "Последняя активность", "Действие"])
        self.users_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 5px;
                font-size: 12px;
                color: #1e293b;
            }
            QTreeWidget::item {
                color: #1e293b;
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #334155;
                color: #ffffff;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)
        layout.addWidget(self.users_tree)

        return widget

    def create_database_tab(self):
        """Вкладка статистики БД."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.db_stats = QTextEdit()
        self.db_stats.setReadOnly(True)
        self.db_stats.setFont(QFont("Courier New", 10))
        self.db_stats.setStyleSheet("""
            QTextEdit {
                background-color: #f0f9ff;
                color: #1e293b;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.db_stats)

        return widget

    def create_system_tab(self):
        """Вкладка системной информации."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self.system_info.setFont(QFont("Courier New", 10))
        self.system_info.setStyleSheet("""
            QTextEdit {
                background-color: #f0fdf4;
                color: #1e293b;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.system_info)

        return widget

    def load_logs(self):
        """Загрузка логов из файлов."""
        self.load_web_logs()
        self.load_desktop_logs()
        self.load_active_users()
        self.load_db_stats()
        self.load_system_info()

    def load_web_logs(self):
        """Загрузка логов веб-портала."""
        # Ищем в нескольких возможных местах
        possible_paths = [
            Path("web_portal.log"),
            Path("logs/web_portal.log"),
            Path("../web_portal.log"),
        ]

        log_file = None
        for path in possible_paths:
            if path.exists():
                log_file = path
                break

        logs_text = ""

        if log_file:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]

                    for line in lines:
                        if 'INFO' in line:
                            color = "#4ade80"
                        elif 'WARNING' in line:
                            color = "#fbbf24"
                        elif 'ERROR' in line:
                            color = "#f87171"
                        else:
                            color = "#94a3b8"

                        logs_text += f'<span style="color: {color}">{line.strip()}</span><br>'
            except Exception as e:
                logs_text = f"❌ Ошибка чтения лога: {e}"
        else:
            logs_text = """
            <div style="padding: 20px; background-color: #fef3c7; border-radius: 8px; border: 1px solid #f59e0b;">
                <p style="color: #92400e; font-weight: bold; margin-bottom: 10px;">
                    ⚠️ Файл логов веб-портала не найден
                </p>
                <p style="color: #78350f; font-size: 13px;">
                    Проверьте что веб-портал запущен и логирование настроено.<br>
                    Ожидаемые пути: web_portal.log или logs/web_portal.log
                </p>
            </div>
            """

        self.web_logs.setHtml(logs_text)

    def load_desktop_logs(self):
        """Загрузка логов СУ."""
        # Ищем в нескольких возможных местах
        possible_paths = [
            Path("logs/app.log"),
            Path("app.log"),
            Path("../logs/app.log"),
        ]

        log_file = None
        for path in possible_paths:
            if path.exists():
                log_file = path
                break

        logs_text = ""

        if log_file:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]

                    for line in lines:
                        if 'INFO' in line:
                            color = "#4ade80"
                        elif 'WARNING' in line:
                            color = "#fbbf24"
                        elif 'ERROR' in line:
                            color = "#f87171"
                        else:
                            color = "#94a3b8"

                        logs_text += f'<span style="color: {color}">{line.strip()}</span><br>'
            except Exception as e:
                logs_text = f"❌ Ошибка чтения лога: {e}"
        else:
            logs_text = """
            <div style="padding: 20px; background-color: #fef3c7; border-radius: 8px; border: 1px solid #f59e0b;">
                <p style="color: #92400e; font-weight: bold; margin-bottom: 10px;">
                    ⚠️ Файл логов СУ не найден
                </p>
                <p style="color: #78350f; font-size: 13px;">
                    Проверьте что приложение запущено и логирование настроено.<br>
                    Ожидаемые пути: logs/app.log или app.log
                </p>
            </div>
            """

        self.desktop_logs.setHtml(logs_text)

    def load_desktop_logs(self):
        """Загрузка логов СУ."""
        # Проверяем несколько возможных путей к логам
        possible_log_files = [
            Path("logs/app.log"),
            Path("app.log"),
            Path("main.log"),
            Path("desktop.log"),
        ]

        log_file = None
        for path in possible_log_files:
            if path.exists():
                log_file = path
                break

        logs_text = ""

        if log_file:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]

                    for line in lines:
                        if 'INFO' in line:
                            color = "#059669"  # Тёмно-зелёный
                        elif 'WARNING' in line:
                            color = "#d97706"  # Тёмно-оранжевый
                        elif 'ERROR' in line:
                            color = "#dc2626"  # Тёмно-красный
                        else:
                            color = "#1e293b"  # Тёмно-серый

                        logs_text += f'<span style="color: {color}">{line.strip()}</span><br>'
            except Exception as e:
                logs_text = f"❌ Ошибка чтения лога: {e}"
        else:
            # Создаём файл логов если его нет
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "app.log"
            log_file.touch()  # Создаём пустой файл

            logs_text = """
            <div style="padding: 20px; background-color: #fef3c7; border-radius: 8px; border: 1px solid #f59e0b;">
                <p style="color: #92400e; font-weight: bold; margin-bottom: 10px;">
                    ⚠️ Файл логов не найден
                </p>
                <p style="color: #78350f; font-size: 13px;">
                    Создан пустой файл: <code>logs/app.log</code><br>
                    Логи будут появляться здесь после запуска приложения.
                </p>
            </div>
            """

        self.desktop_logs.setHtml(logs_text)

    def load_active_users(self):
        """Загрузка информации об активных пользователях."""
        self.users_tree.clear()

        try:
            from models.user import User
            from models.audit_log import AuditLog

            # Получаем последних активных пользователей
            recent_users = self.db.query(User).limit(20).all()

            for user in recent_users:
                # Получаем последнее действие
                last_action = self.db.query(AuditLog).filter(
                    AuditLog.user_info.contains(user.username)
                ).order_by(AuditLog.timestamp.desc()).first()

                item = QTreeWidgetItem([
                    user.full_name,
                    user.role.value,
                    user.last_login.strftime("%d.%m.%Y %H:%M") if user.last_login else "Никогда",
                    last_action.action_type.value if last_action else "—"
                ])

                # Цвет в зависимости от активности (тёмные цвета для читаемости)
                if user.last_login and (datetime.now() - user.last_login).days < 1:
                    item.setForeground(0, QColor("#059669"))  # Тёмно-зелёный - активен сегодня
                else:
                    item.setForeground(0, QColor("#1e293b"))  # Тёмно-серый - неактивен

                self.users_tree.addTopLevelItem(item)

            self.users_tree.resizeColumnToContents(0)
            self.users_tree.resizeColumnToContents(1)
            self.users_tree.resizeColumnToContents(2)
            self.users_tree.resizeColumnToContents(3)

        except Exception as e:
            item = QTreeWidgetItem(["❌ Ошибка загрузки", str(e), "", ""])
            self.users_tree.addTopLevelItem(item)

    def load_db_stats(self):
        """Загрузка статистики БД."""
        stats_text = "📊 СТАТИСТИКА БАЗЫ ДАННЫХ\n"
        stats_text += "=" * 60 + "\n\n"

        try:
            from models.car import Car
            from models.client import Client
            from models.agreement import RentalAgreement
            from models.user import User
            from models.support_request import SupportRequest

            # Количество записей
            stats_text += f"🚗 Автомобили: {self.db.query(Car).count()}\n"
            stats_text += f"👥 Клиенты: {self.db.query(Client).count()}\n"
            stats_text += f"👤 Пользователи: {self.db.query(User).count()}\n"
            stats_text += f"📋 Договоры: {self.db.query(RentalAgreement).count()}\n"
            stats_text += f"📩 Обращения: {self.db.query(SupportRequest).count()}\n\n"

            # Активные аренды
            from models.agreement import AgreementStatus
            active_rentals = self.db.query(RentalAgreement).filter(
                RentalAgreement.status == AgreementStatus.ACTIVE
            ).count()
            stats_text += f"🔥 Активных аренд: {active_rentals}\n"

            # Просроченные
            from datetime import date
            overdue = self.db.query(RentalAgreement).filter(
                RentalAgreement.status == AgreementStatus.ACTIVE,
                RentalAgreement.end_date < date.today()
            ).count()
            stats_text += f"⚠️ Просроченных: {overdue}\n\n"

            # Последние действия
            stats_text += "🕐 ПОСЛЕДНИЕ ДЕЙСТВИЯ:\n"
            stats_text += "-" * 40 + "\n"

            from models.audit_log import AuditLog
            recent_logs = self.db.query(AuditLog).order_by(
                AuditLog.timestamp.desc()
            ).limit(10).all()

            for log in recent_logs:
                time_str = log.timestamp.strftime("%H:%M:%S") if log.timestamp else "—"
                stats_text += f"{time_str} | {log.action_type.value} | {log.entity_name}\n"

        except Exception as e:
            stats_text += f"❌ Ошибка: {e}"

        self.db_stats.setPlainText(stats_text)

    def load_system_info(self):
        """Загрузка системной информации."""
        import psutil
        import platform

        info_text = "💻 СИСТЕМНАЯ ИНФОРМАЦИЯ\n"
        info_text += "=" * 60 + "\n\n"

        # ОС
        info_text += f"Операционная система: {platform.system()} {platform.release()}\n"
        info_text += f"Python версия: {platform.python_version()}\n\n"

        # CPU
        info_text += f"Загрузка CPU: {psutil.cpu_percent(interval=1)}%\n"
        info_text += f"Ядер CPU: {psutil.cpu_count()}\n\n"

        # RAM
        memory = psutil.virtual_memory()
        info_text += f"Использование RAM: {memory.percent}%\n"
        info_text += f"Доступно: {memory.available / 1024 / 1024 / 1024:.1f} GB\n\n"

        # Disk
        disk = psutil.disk_usage('/')
        info_text += f"Диск: {disk.percent}% использовано\n"
        info_text += f"Свободно: {disk.free / 1024 / 1024 / 1024:.1f} GB\n"

        self.system_info.setPlainText(info_text)

    def on_filter_changed(self, value):
        """Обработка изменения фильтра."""
        self.current_filter = value
        self.load_logs()

    def clear_logs(self):
        """Очистка логов."""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Очистить все логи?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Очистка файлов логов
            for log_file in ["web_portal.log", "logs/app.log"]:
                path = Path(log_file)
                if path.exists():
                    path.write_text("")

            self.load_logs()
            QMessageBox.information(self, "Успех", "Логи очищены")

    def export_logs(self):
        """Экспорт логов в файл."""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт логов", "logs_export.txt", "Text Files (*.txt)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.web_logs.toPlainText())
                    f.write("\n\n" + "=" * 60 + "\n\n")
                    f.write(self.desktop_logs.toPlainText())

                QMessageBox.information(self, "Успех", f"Логи экспортированы в {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать: {e}")

    def closeEvent(self, event):
        self.refresh_timer.stop()
        self.db.close()
        super().closeEvent(event)