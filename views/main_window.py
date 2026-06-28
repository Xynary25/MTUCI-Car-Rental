from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QStackedWidget, QStatusBar, QLabel, QFrame, QApplication,
                             QPushButton, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
import os
import json

from database import SessionLocal
from utils.theme_manager import get_theme
from views.notification_view import NotificationWidget
from utils.signals import global_signals
from models.user import User, UserRole
from views.dev_console import DevConsoleDialog
from utils.logger import app_logger, log_user_action


class MainWindow(QMainWindow):
    """Главное окно приложения AutoRent Pro."""

    def __init__(self, current_user: User = None):
        super().__init__()
        self.current_user = current_user
        self.current_theme = "light"
        self.current_font_size = 13
        self.settings_file = "settings.json"

        self.settings = self.load_settings()
        self.current_theme = self.settings.get("theme", "light")
        self.current_font_size = self.settings.get("font_size", 13)

        self.setWindowTitle("AutoRent Pro | Система управления арендой автомобилей")
        self.resize(1400, 900)
        self.setMinimumSize(800, 600)  # Минимальный размер окна

        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        global_signals.navigate_to_agreement.connect(self.show_agreement)

        # СНАЧАЛА инициализируем интерфейс (создаём status_bar)
        self.init_ui()

        # ПОТОМ применяем тему и шрифт
        self.apply_theme(self.current_theme)
        self.apply_font_size(self.current_font_size)

        if current_user:
            self.status_bar.showMessage(
                f"✓ {current_user.full_name} ({current_user.role.value}) | AutoRent Pro v1.0"
            )

    def load_settings(self) -> dict:
        """Загрузка настроек приложения из файла."""
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

    def init_ui(self):
        """Инициализация главного интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === Боковая панель ===
        sidebar_frame = QFrame()
        sidebar_frame.setMinimumWidth(250)
        sidebar_frame.setMaximumWidth(350)
        sidebar_frame.setObjectName("sidebar_frame")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Логотип
        logo_label = QLabel("🚗 AutoRent Pro")
        logo_label.setObjectName("logo_label")
        sidebar_layout.addWidget(logo_label)

        # Информация о текущем пользователе + кнопка смены темы
        if self.current_user:
            user_info_frame = QFrame()
            user_info_frame.setObjectName("user_info_frame")
            user_info_layout = QVBoxLayout(user_info_frame)
            user_info_layout.setContentsMargins(15, 10, 15, 10)
            user_info_layout.setSpacing(5)

            user_name_label = QLabel(self.current_user.full_name)
            user_name_label.setObjectName("user_name_label")
            user_name_label.setWordWrap(True)
            user_info_layout.addWidget(user_name_label)

            user_role_label = QLabel(f"Роль: {self.current_user.role.value}")
            user_role_label.setObjectName("user_role_label")
            user_info_layout.addWidget(user_role_label)

            # Кнопка смены темы (доступна всем ролям)
            theme_toggle_btn = QPushButton(" Тёмная тема" if self.current_theme == "light" else "☀️ Светлая тема")
            theme_toggle_btn.setObjectName("theme_toggle_btn")
            theme_toggle_btn.setMinimumHeight(35)
            theme_toggle_btn.clicked.connect(self.toggle_theme)
            user_info_layout.addWidget(theme_toggle_btn)

            sidebar_layout.addWidget(user_info_frame)

        # Меню навигации
        self.sidebar = QListWidget()

        # Сохраняем индексы для навигации
        self._menu_indices = {}

        # Основные пункты меню
        menu_items = [
            ("📊 Дашборд", 0),
            ("🚗 Автопарк", 1),
            ("👥 Клиенты", 2),
            ("📝 Договоры", 3),
            ("⚠️ Штрафы", 4),
            ("🔧 ТО", 5),
            ("🔔 Уведомления", 6),
            (" Календарь", 7),
            ("📈 Статистика", 8),
            ("📑 Отчёты", 9),
            ("🔍 Аудит", 10),
            ("⚙️ Настройки", 11),
        ]

        # Добавляем основные пункты
        for item_text, index in menu_items:
            self.sidebar.addItem(item_text)
            self._menu_indices[item_text] = index

        # Добавляем пункт "Пользователи" только для администраторов
        users_index = None
        if self.current_user and self.current_user.has_permission('view_users'):
            users_index = self.sidebar.count()
            self.sidebar.addItem("👤 Пользователи")
            self._menu_indices["👤 Пользователи"] = users_index


        # Служебные пункты
        about_index = self.sidebar.count()
        self.sidebar.addItem("ℹ️ О программе")
        self._menu_indices["ℹ️ О программе"] = about_index

        # Добавляем консоль разработчика только для админов
        dev_console_index = None
        if self.current_user and self.current_user.role.value in ['superadmin', 'admin']:
            dev_console_index = self.sidebar.count()
            self.sidebar.addItem("🐞 Консоль разработчика")
            self._menu_indices["🐞 Консоль разработчика"] = dev_console_index

        # Сохраняем индексы для использования в on_menu_changed
        self._about_index = about_index
        self._dev_console_index = dev_console_index
        self._users_index = users_index

        # Уменьшаем высоту элементов списка
        self.sidebar.setStyleSheet("""
            QListWidget::item {
                padding: 8px 15px;
                min-height: 35px;
            }
        """)

        self.sidebar.currentRowChanged.connect(self.on_menu_changed)
        sidebar_layout.addWidget(self.sidebar)

        # Кнопка выхода из аккаунта
        logout_btn = QPushButton("🚪 Выйти из аккаунта")
        logout_btn.setObjectName("logout_btn")
        logout_btn.setMinimumHeight(45)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton#logout_btn {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                margin: 10px 15px;
            }
            QPushButton#logout_btn:hover {
                background-color: #DC2626;
            }
        """)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar_frame)

        # === Основная область контента ===
        content_frame = QWidget()
        content_frame.setObjectName("content_frame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(20)

        self.header_label = QLabel("Добро пожаловать в AutoRent Pro!")
        self.header_label.setObjectName("header_label")
        content_layout.addWidget(self.header_label)

        self.content_stack = QStackedWidget()

        try:
            from views.dashboard_view import DashboardWidget
            from views.car_view import CarWidget
            from views.client_view import ClientWidget
            from views.agreement_view import AgreementWidget
            from views.penalty_view import PenaltyWidget
            from views.maintenance_view import MaintenanceWidget
            from views.calendar_view import CalendarWidget
            from views.statistics_view import StatisticsWidget
            from views.report_view import ReportWidget
            from views.audit_view import AuditWidget
            from views.settings_view import SettingsWidget
            from views.users_view import UsersWidget

            # Передаём current_user во все виджеты
            self.content_stack.addWidget(DashboardWidget(current_user=self.current_user))  # 0
            self.content_stack.addWidget(CarWidget(current_user=self.current_user))  # 1
            self.content_stack.addWidget(ClientWidget(current_user=self.current_user))  # 2
            self.content_stack.addWidget(AgreementWidget(current_user=self.current_user))  # 3
            self.penalty_widget = PenaltyWidget(current_user=self.current_user)  # 4
            self.content_stack.addWidget(self.penalty_widget)
            self.maintenance_widget = MaintenanceWidget(current_user=self.current_user)  # 5
            self.content_stack.addWidget(self.maintenance_widget)
            self.notification_widget = NotificationWidget(current_user=self.current_user)  # 6
            self.content_stack.addWidget(self.notification_widget)
            self.calendar_widget = CalendarWidget(current_user=self.current_user)  # 7
            self.content_stack.addWidget(self.calendar_widget)
            self.content_stack.addWidget(StatisticsWidget(current_user=self.current_user))  # 8
            self.content_stack.addWidget(ReportWidget(current_user=self.current_user))  # 9
            self.content_stack.addWidget(AuditWidget(current_user=self.current_user))  # 10
            self.content_stack.addWidget(SettingsWidget(self, current_user=self.current_user))  # 11

            # Добавляем виджет пользователей если есть права
            if users_index is not None:
                self.users_widget = UsersWidget(current_user=self.current_user)
                self.content_stack.addWidget(self.users_widget)

            # Заглушка для "О программе" (всегда добавляется)
            about_placeholder = QWidget()
            about_layout = QVBoxLayout(about_placeholder)
            about_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            about_label = QLabel("Нажмите 'О программе' в меню")
            about_label.setStyleSheet("font-size: 18px; color: #94a3b8;")
            about_layout.addWidget(about_label)
            self.content_stack.addWidget(about_placeholder)

            # Заглушка для "Консоль разработчика" (добавляется только если есть пункт меню)
            if dev_console_index is not None:
                dev_placeholder = QWidget()
                dev_layout = QVBoxLayout(dev_placeholder)
                dev_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dev_label = QLabel("Нажмите 'Консоль разработчика' в меню")
                dev_label.setStyleSheet("font-size: 18px; color: #94a3b8;")
                dev_layout.addWidget(dev_label)
                self.content_stack.addWidget(dev_placeholder)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Ошибка загрузки модулей: {error_details}")
            error_label = QLabel(f"Ошибка загрузки модулей: {str(e)}")
            self.content_stack.addWidget(error_label)

        content_layout.addWidget(self.content_stack, stretch=1)
        main_layout.addWidget(content_frame, stretch=1)
        content_layout.addStretch()

        # === Строка состояния ===
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✓ Готово к работе | AutoRent Pro v1.0")

    def apply_theme(self, theme_name: str):
        """Глобальное применение темы через QApplication."""
        self.current_theme = theme_name
        qss = get_theme(theme_name)
        QApplication.instance().setStyleSheet(qss)

        if theme_name == "dark":
            self.header_label.setStyleSheet("""
                QLabel#header_label {
                    font-size: 28px;
                    font-weight: bold;
                    color: #E2E8F0;
                }
            """)
        else:
            self.header_label.setStyleSheet("""
                QLabel#header_label {
                    font-size: 28px;
                    font-weight: bold;
                    color: #1E293B;
                }
            """)

        self.status_bar.showMessage(
            f"✓ Тема '{'Темная' if theme_name == 'dark' else 'Светлая'}' активирована"
        )

    def apply_font_size(self, size: int):
        """Изменение размера шрифта глобально."""
        self.current_font_size = size
        font = QApplication.font()
        font.setPointSize(size)
        QApplication.setFont(font)
        self.status_bar.showMessage(f"✓ Размер шрифта изменён на {size}pt")

    def toggle_theme(self):
        """Переключение темы оформления."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            # Кнопка смены темы находится в user_info_frame, не в sidebar
            pass

        user_info_frame = None
        for widget in self.findChildren(QFrame):
            if widget.objectName() == "user_info_frame":
                user_info_frame = widget
                break

        if user_info_frame:
            for btn in user_info_frame.findChildren(QPushButton):
                if btn.objectName() == "theme_toggle_btn":
                    btn.setText("🌙 Тёмная тема" if new_theme == "light" else "☀️ Светлая тема")
                    break

    def on_menu_changed(self, index: int):
        """Обработка выбора пункта меню."""
        # Проверяем служебные пункты по сохраненным индексам
        if index == self._about_index:
            # "О программе" - открываем диалог
            from views.about_dialog import AboutDialog
            dialog = AboutDialog(self)
            dialog.exec()
            # Возвращаем выделение на предыдущий пункт или на дашборд
            self.sidebar.setCurrentRow(0)
            return

        if self._dev_console_index is not None and index == self._dev_console_index:
            # "Консоль разработчика" - открываем диалог
            from views.dev_console import DevConsoleDialog
            dialog = DevConsoleDialog(self)
            dialog.exec()
            # Возвращаем выделение на предыдущий пункт или на дашборд
            self.sidebar.setCurrentRow(0)
            return

        # Обычное переключение вкладок
        if 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
            section_name = self.sidebar.item(index).text()
            self.status_bar.showMessage(f"📂 Раздел: {section_name}")

    def logout(self):
        """Выход из системы."""
        # Логируем выход
        log_user_action(
            user_id=self.current_user.id,
            username=self.current_user.username,
            action="LOGOUT",
            details="User logged out from desktop app"
        )

        app_logger.info(f"Main window closed by {self.current_user.username}")
        try:
            # Закрываем все базы данных перед выходом
            self.close_all_database_connections()

            # Очищаем текущую сессию
            if hasattr(self, 'current_user'):
                # Логируем выход
                from database import SessionLocal
                from models.audit_log import AuditLog, ActionType
                db = SessionLocal()
                try:
                    log = AuditLog(
                        action_type=ActionType.LOGOUT,
                        entity_name="User",
                        entity_id=self.current_user.id,
                        description=f"Пользователь {self.current_user.username} вышел из системы",
                        user_info=f"{self.current_user.username} ({self.current_user.role.value})"
                    )
                    db.add(log)
                    db.commit()
                except Exception as e:
                    print(f"Ошибка логирования выхода: {e}")
                finally:
                    db.close()

            # Закрываем главное окно
            self.close()

            # Показываем окно входа заново
            from views.login_dialog import LoginDialog
            login_dialog = LoginDialog()
            if login_dialog.exec() == LoginDialog.DialogCode.Accepted:
                new_user = login_dialog.get_user()
                if new_user:
                    new_window = MainWindow(current_user=new_user)
                    new_window.show()
        except Exception as e:
            print(f"Ошибка при выходе: {e}")
            import sys
            sys.exit(1)

    def closeEvent(self, event):
        """Закрытие виджета уведомлений."""
        if hasattr(self, 'check_timer'):
            self.check_timer.stop()
            print("Таймер уведомлений остановлен в closeEvent")
        if hasattr(self, 'db'):
            self.db.close()
            print("Сессия БД уведомлений закрыта")
        super().closeEvent(event)

    def close_all_database_connections(self):
        """Закрытие всех соединений с базой данных."""
        try:
            from database import engine
            engine.dispose()  # Закрываем все соединения в пуле

            # Закрываем сессии всех виджетов
            for i in range(self.content_stack.count()):
                widget = self.content_stack.widget(i)
                if widget and hasattr(widget, 'db'):
                    try:
                        widget.db.close()
                        print(f"Закрыта сессия виджета: {widget.__class__.__name__}")
                    except Exception as e:
                        print(f"Ошибка закрытия сессии {widget.__class__.__name__}: {e}")

            # Закрываем сессию уведомлений
            if hasattr(self, 'notification_widget') and self.notification_widget:
                try:
                    self.notification_widget.db.close()
                    # Останавливаем таймер уведомлений
                    if hasattr(self.notification_widget, 'check_timer'):
                        self.notification_widget.check_timer.stop()
                        print("Таймер уведомлений остановлен")
                except Exception as e:
                    print(f"Ошибка закрытия сессии уведомлений: {e}")

            print("Все соединения с БД закрыты")
        except Exception as e:
            print(f"Критическая ошибка при закрытии соединений: {e}")

    def close_all_database_connections(self):
        """Закрытие всех соединений с базой данных."""
        # Закрываем виджеты которые используют БД
        for i in range(self.content_stack.count()):
            widget = self.content_stack.widget(i)
            if widget and hasattr(widget, 'db'):
                try:
                    widget.db.close()
                except:
                    pass

    def restart_backup_scheduler(self, settings: dict):
        """Перезапуск планировщика бэкапов с новыми настройками."""
        from utils.backup_scheduler import backup_scheduler
        from utils.system_utils import cleanup_old_backups
        import time

        backup_scheduler.stop()
        time.sleep(0.5)

        if settings.get("auto_backup", False):
            success = backup_scheduler.start(
                backup_dir=settings.get("backup_path", "./backups"),
                frequency=settings.get("auto_backup_frequency", "daily"),
                hour=settings.get("auto_backup_hour", 23),
                minute=settings.get("auto_backup_minute", 0),
                day_of_week=settings.get("auto_backup_day", 0),
                max_backups=settings.get("max_backups", 10)
            )

            if success:
                self.status_bar.showMessage("✓ Настройки резервного копирования обновлены")
            else:
                self.status_bar.showMessage("✗ Ошибка запуска планировщика")
        else:
            self.status_bar.showMessage("✓ Автоматическое резервное копирование отключено")

    def show_agreement(self, agreement_id: int):
        """Показать договор по ID."""
        for i in range(self.sidebar.count()):
            item_text = self.sidebar.item(i).text()
            if "Договор" in item_text or "" in item_text:
                self.content_stack.setCurrentIndex(i)
                self.sidebar.setCurrentRow(i)

                agreement_widget = self.content_stack.widget(i)
                if agreement_widget and hasattr(agreement_widget, 'highlight_agreement'):
                    agreement_widget.highlight_agreement(agreement_id)
                break