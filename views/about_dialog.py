from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QFrame, QTabWidget, QWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AboutDialog(QDialog):
    """Диалог «О программе» с инструкцией по вкладкам."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе AutoRent Pro")
        self.resize(1100, 750)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        header_frame = QFrame()
        header_frame.setObjectName("about_header_frame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)

        icon_label = QLabel("🚗")
        icon_label.setObjectName("about_icon")
        icon_label.setStyleSheet("font-size: 48px;")
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_label = QLabel("AutoRent Pro")
        title_label.setObjectName("about_title")
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2563EB;")
        title_layout.addWidget(title_label)

        version_label = QLabel("Версия 1.0.0 | Система управления арендой автомобилей")
        version_label.setObjectName("about_version")
        version_label.setStyleSheet("font-size: 14px; color: #64748B;")
        title_layout.addWidget(version_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("about_separator")
        separator.setStyleSheet("background-color: #E2E8F0; max-height: 2px;")
        layout.addWidget(separator)

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setObjectName("about_tabs")
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                padding: 10px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                border-bottom: 3px solid transparent;
            }
            QTabBar::tab:selected {
                border-bottom: 3px solid #2563EB;
                color: #2563EB;
            }
        """)

        # Вкладка 1: О системе (РАСШИРЕНА)
        self.tabs.addTab(self._create_about_tab(), "ℹ️ О системе")

        # Вкладка 2: Веб-портал DriveControl (НОВАЯ)
        self.tabs.addTab(self._create_web_portal_tab(), "🌐 Веб-портал")

        # Вкладка 3: Система поддержки (НОВАЯ)
        self.tabs.addTab(self._create_support_system_tab(), "💬 Поддержка")

        # Вкладка 4: Роли и права (таблица)
        self.tabs.addTab(self._create_permissions_tab(), "🔐 Роли и права")

        # Вкладка 5: Инструкция (РАСШИРЕНА)
        self.tabs.addTab(self._create_instruction_tab(), "📖 Инструкция")

        # Вкладка 6: Контакты (ОБНОВЛЕНА)
        self.tabs.addTab(self._create_contacts_tab(), "✉️ Контакты")

        layout.addWidget(self.tabs, stretch=1)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(45)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    # ========================================================================
    # ВКЛАДКА 1: О СИСТЕМЕ (РАСШИРЕННАЯ)
    # ========================================================================
    def _create_about_tab(self) -> QWidget:
        """Вкладка «О системе» с полной структурой проекта."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # === Основная информация ===
        info_group = QFrame()
        info_group.setObjectName("about_info_group")
        info_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #F8FAFC;
            }
        """)
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(10)

        info_layout.addWidget(self._make_info_row("Название:", "AutoRent Pro + DriveControl"))
        info_layout.addWidget(self._make_info_row("Версия:", "1.0.0"))
        info_layout.addWidget(self._make_info_row(
            "Описание:",
            "Комплексная информационная система управления арендой легковых автомобилей. "
            "Включает десктопную СУ (AutoRent Pro) для сотрудников и веб-портал (DriveControl) "
            "для клиентов и администраторов. Автоматизирует процессы учёта автопарка, клиентов, "
            "договоров аренды, финансового учёта и отчётности."
        ))
        info_layout.addWidget(self._make_info_row("Разработчики:", "Студенты МТУСИ, кафедра «Программная инженерия»"))
        info_layout.addWidget(self._make_info_row("Год разработки:", "2026"))
        info_layout.addWidget(self._make_info_row("Учебная практика:", "Технологическая практика МТУСИ"))

        layout.addWidget(info_group)

        # === Архитектура системы ===
        arch_group = QFrame()
        arch_group.setObjectName("about_info_group")
        arch_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #FEF3C7;
            }
        """)
        arch_layout = QVBoxLayout(arch_group)
        arch_layout.setSpacing(10)

        arch_title = QLabel("🏗️ Архитектура системы")
        arch_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #92400E;")
        arch_layout.addWidget(arch_title)

        arch_items = [
            ("Десктопная СУ (AutoRent Pro):", "PyQt6 + SQLAlchemy + SQLite/PostgreSQL"),
            ("Веб-портал (DriveControl):", "FastAPI + Jinja2 + Uvicorn"),
            ("Общая база данных:", "rental.db (SQLite) — общая для обоих приложений"),
            ("Синхронизация:", "Автоматическая синхронизация фото и данных между СУ и веб"),
            ("Безопасность:", "RBAC, хеширование SHA-256 с солью, аудит-лог"),
        ]

        for label, value in arch_items:
            arch_layout.addWidget(self._make_info_row(label, value))

        layout.addWidget(arch_group)

        # === Система автообновления ===
        refresh_group = QFrame()
        refresh_group.setObjectName("about_info_group")
        refresh_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #D1FAE5;
            }
        """)
        refresh_layout = QVBoxLayout(refresh_group)
        refresh_layout.setSpacing(10)

        refresh_title = QLabel("🔄 Система автообновления")
        refresh_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #065F46;")
        refresh_layout.addWidget(refresh_title)

        refresh_items = [
            ("Дашборд:", "Автообновление каждые 30 секунд"),
            ("Уведомления:", "Проверка новых уведомлений каждые 5 минут"),
            ("Консоль разработчика:", "Автообновление логов каждые 3 секунды"),
        ]

        for label, value in refresh_items:
            refresh_layout.addWidget(self._make_info_row(label, value))

        layout.addWidget(refresh_group)

        # === Структура проекта ===
        struct_group = QFrame()
        struct_group.setObjectName("about_info_group")
        struct_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #F0FDF4;
            }
        """)
        struct_layout = QVBoxLayout(struct_group)
        struct_layout.setSpacing(10)

        struct_title = QLabel("📁 Структура проекта")
        struct_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #166534;")
        struct_layout.addWidget(struct_title)

        struct_text = QLabel("MTUCI-Rental-Car/\n"
    "├── .env                             # Переменные окружения\n"
    "├── .gitignore                       # Исключения для Git\n"
    "├── check_db.py                      # Скрипт проверки БД\n"
    "├── config.py                        # Общие настройки\n"
    "├── database.py                      # Конфигурация БД (СУ)\n"
    "├── db_operation_pending.json        # Флаг операций с БД\n"
    "├── fix_enum.py                      # Скрипт исправления Enum\n"
    "├── icon.png                         # Иконка приложения\n"
    "├── main.py                          # Точка входа десктопной СУ\n"
    "├── rental.db                        # База данных SQLite\n"
    "├── requirements.txt                 # Зависимости Python\n"
    "├── settings.json                    # Настройки приложения\n"
    "│\n"
    "├── assets/                          # Ресурсы приложения\n"
    "── backups/                         # Резервные копии БД\n"
    "│\n"
    "├── controllers/                     # Контроллеры (бизнес-логика)\n"
    "│   ├── __init__.py\n"
    "│   ├── agreement_controller.py      # Договоры\n"
    "│   ├── calendar_controller.py       # Календарь\n"
    "│   ├── car_controller.py            # Автомобили\n"
    "│   ├── client_controller.py         # Клиенты\n"
    "│   ├── maintenance_controller.py    # ТО\n"
    "│   ├── penalty_controller.py        # Штрафы\n"
    "│   └── report_controller.py         # Отчёты\n"
    "│\n"
    "├── images/                          # Фото автомобилей (синхронизация с веб)\n"
    "│\n"
    "├── logs/                            # Логи десктопной СУ\n"
    "│   ├── app.log                      # Основной лог\n"
    "│   ├── audit.log                    # Журнал аудита\n"
    "│   └── web_portal.log               # Логи веб-портала\n"
    "│\n"
    "── models/                          # Модели SQLAlchemy\n"
    "│   ├── __init__.py\n"
    "│   ├── agreement.py                 # Договоры аренды\n"
    "│   ├── audit_log.py                 # Журнал аудита\n"
    "│   ├── car.py                       # Автомобили\n"
    "│   ├── client.py                    # Клиенты\n"
    "│   ├── expense.py                   # Расходы\n"
    "│   ├── maintenance.py               # ТО\n"
    "│   ├── notification.py              # Уведомления\n"
    "│   ├── payment.py                   # Платежи\n"
    "│   ├── penalty.py                   # Штрафы\n"
    "│   ├── return_request.py            # Запросы на возврат\n"
    "│   ├── support_message.py           # Сообщения поддержки\n"
    "│   ├── support_request.py           # Обращения в поддержку\n"
    "│   └── user.py                      # Пользователи\n"
    "│\n"
    "├── utils/                           # Утилиты\n"
    "│   ├── __init__.py\n"
    "│   ├── auth_service.py              # Аутентификация\n"
    "│   ├── backup_scheduler.py          # Планировщик бэкапов\n"
    "│   ├── db_migrate.py                # Миграция БД\n"
    "│   ├── db_operation_flag.py         # Флаги операций БД\n"
    "│   ├── dev_console.py               # Логирование dev-консоли\n"
    "│   ├── fix_audit_logs.py            # Исправление логов аудита\n"
    "│   ├── image_utils.py               # Работа с изображениями\n"
    "│   ├── logger.py                    # Централизованное логирование\n"
    "│   ├── notification_service.py      # Сервис уведомлений\n"
    "│   ├── path_utils.py                # Утилиты путей\n"
    "│   ├── pdf_generator.py             # Генерация PDF\n"
    "│   ├── permissions.py               # Система прав доступа\n"
    "│   ├── seeder.py                    # Наполнение БД тестовыми данными\n"
    "│   ├── signals.py                   # Глобальные сигналы\n"
    "│   ├── system_utils.py              # Системные утилиты\n"
    "│   ├── table_utils.py               # Утилиты таблиц\n"
    "│   ── theme_manager.py             # Управление темами\n"
    "│\n"
    "├── views/                           # PyQt6 виджеты\n"
    "│   ├── logs/                        # Логи виджетов\n"
    "│   ├── widgets/                     # Дополнительные виджеты\n"
    "│   ├── __init__.py\n"
    "│   ├── about_dialog.py              # Диалог «О программе»\n"
    "│   ├── agreement_view.py            # Виджет договоров\n"
    "│   ├── audit_view.py                # Виджет аудита\n"
    "│   ├── calendar_view.py             # Виджет календаря\n"
    "│   ├── car_detail_dialog.py         # Диалог деталей авто\n"
    "│   ├── car_view.py                  # Виджет автопарка\n"
    "│   ├── change_password_dialog.py    # Диалог смены пароля\n"
    "│   ├── client_view.py               # Виджет клиентов\n"
    "│   ├── dashboard_view.py            # Виджет дашборда\n"
    "│   ├── db_management_dialog.py      # Диалог управления БД\n"
    "│   ├── dev_console.py               # Консоль разработчика\n"
    "│   ├── login_dialog.py              # Диалог входа\n"
    "│   ├── main_window.py               # Главное окно\n"
    "│   ├── maintenance_view.py          # Виджет ТО\n"
    "│   ├── notification_view.py         # Виджет уведомлений\n"
    "│   ├── penalty_view.py              # Виджет штрафов\n"
    "│   ├── report_view.py               # Виджет отчётов\n"
    "│   ├── settings_view.py             # Виджет настроек\n"
    "│   ├── statistics_view.py           # Виджет статистики\n"
    "│   ├── user_edit_dialog.py          # Диалог редактирования пользователя\n"
    "│   └── users_view.py                # Виджет пользователей\n"
    "│\n"
    "── web_portal/                      # Веб-портал DriveControl (FastAPI)\n"
    "│   ├── logs/                        # Логи веб-портала\n"
    "│   ├── static/                      # Статические файлы\n"
    "│   │   ├── car_images/              # Фото автомобилей\n"
    "│   │   └── support_attachments/     # Прикреплённые файлы обращений\n"
    "│   ├── templates/                   # Jinja2 шаблоны\n"
    "│   │   ├── admin.html               # Админ-панель (пользователи)\n"
    "│   │   ├── admin_cars.html          # Управление автопарком\n"
    "│   │   ├── admin_maintenance.html   # Управление ТО\n"
    "│   │   ├── admin_reports.html       # Отчёты админа\n"
    "│   │   ├── admin_return_requests.html  # Запросы на возврат\n"
    "│   │   ├── admin_support_request_detail.html  # Детали обращения (админ)\n"
    "│   │   ├── admin_support_requests.html        # Список обращений (админ)\n"
    "│   │   ├── admin_user_detail.html   # Профиль пользователя (админ)\n"
    "│   │   ├── car_detail.html          # Страница автомобиля\n"
    "│   │   ├── dev_logs.html            # Консоль логов разработчика\n"
    "│   │   ├── index.html               # Главная страница\n"
    "│   │   ├── payments.html            # Страница платежей\n"
    "│   │   ├── profile.html             # Профиль клиента\n"
    "│   │   ├── rules.html               # Правила и договоры\n"
    "│   │   ├── support_request_detail.html        # Детали обращения (клиент)\n"
    "│   │   └── user_support_requests.html         # Обращения клиента\n"
    "│   ├── alembic_migration.py         # Миграции Alembic\n"
    "│   ├── client.py                    # Модель клиента для веб\n"
    "│   ├── create_notification_reads_table.py  # Создание таблицы прочтений\n"
    "│   ├── database.py                  # Подключение к БД (веб)\n"
    "│   ├── main.py                      # FastAPI приложение\n"
    "│   ├── migrate_db.py                # Скрипт миграции БД\n"
    "│   ├── migrate_return_requests.py   # Миграция запросов на возврат\n"
    "│   ├── requirements.txt             # Зависимости веб-портала\n"
    "│   ├── return_request.py            # Модель запроса на возврат\n"
    "│   ├── support_request.py           # Модель обращения в поддержку\n"
    "│   ├── web_models.py                # Модели для веб-портала\n"
    "│   └── web_portal.log               # Лог веб-портала\n"
    "│\n"
    "└── External Libraries/              # Внешние библиотеки (PyCharm)\n"
    "    └── Scratches and Consoles/      # Скретчи и консоли (PyCharm)"
)
        struct_text.setStyleSheet(
            "font-size: 12px; color: #14532D; font-family: 'Courier New', monospace; line-height: 1.4;")
        struct_text.setWordWrap(True)
        struct_layout.addWidget(struct_text)

        layout.addWidget(struct_group)

        # === Технологический стек (РАСШИРЕННЫЙ) ===
        tech_group = QFrame()
        tech_group.setObjectName("about_info_group")
        tech_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #F8FAFC;
            }
        """)
        tech_layout = QVBoxLayout(tech_group)
        tech_layout.setSpacing(10)

        tech_title = QLabel("🛠️ Технологический стек")
        tech_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563EB;")
        tech_layout.addWidget(tech_title)

        tech_items = [
            ("Язык программирования:", "Python 3.10+"),
            ("Графический интерфейс (СУ):", "PyQt6 6.11.0 (фреймворк Qt6)"),
            ("Веб-фреймворк:", "FastAPI 0.137.1 + Uvicorn 0.49.0"),
            ("Шаблонизатор:", "Jinja2 3.1.6"),
            ("ORM:", "SQLAlchemy 2.0.51"),
            ("База данных:", "SQLite (по умолчанию), PostgreSQL (опционально, psycopg2 2.9.12)"),
            ("Обработка изображений:", "Pillow 12.2.0"),
            ("Генерация PDF:", "ReportLab 4.5.1"),
            ("Планировщик задач:", "APScheduler 3.11.2"),
            ("Валидация форм:", "Pydantic 2.13.4"),
            ("Загрузка файлов:", "python-multipart 0.0.32"),
            ("Миграции БД:", "Alembic 1.18.4"),
            ("Архитектура:", "MVC (Model-View-Controller)"),
            ("Система безопасности:", "RBAC (Role-Based Access Control)"),
        ]

        for label, value in tech_items:
            tech_layout.addWidget(self._make_info_row(label, value))

        layout.addWidget(tech_group)

        # === Реализованный функционал (РАСШИРЕННЫЙ) ===
        features_group = QFrame()
        features_group.setObjectName("about_info_group")
        features_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #F8FAFC;
            }
        """)
        features_layout = QVBoxLayout(features_group)
        features_layout.setSpacing(10)

        features_title = QLabel("✅ Реализованный функционал")
        features_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563EB;")
        features_layout.addWidget(features_title)

        # Подзаголовок: Десктопная СУ
        sub1 = QLabel("🖥️ Десктопная СУ (AutoRent Pro):")
        sub1.setStyleSheet("font-size: 14px; font-weight: bold; color: #059669; margin-top: 5px;")
        features_layout.addWidget(sub1)

        features_desktop = [
            "• Полный CRUD для автомобилей, клиентов, договоров",
            "• Система ролей и прав доступа (SuperAdmin, Admin, Manager, Operator)",
            "• Индивидуальная настройка прав для каждого пользователя",
            "• Автоматический расчёт стоимости аренды со скидками",
            "• Проверка доступности автомобиля на запрашиваемые даты",
            "• Экспорт договоров в PDF (одним файлом или отдельными)",
            "• Экспорт отчётов в CSV с поддержкой кириллицы",
            "• Учёт штрафов и повреждений с привязкой к договорам",
            "• Управление техническим обслуживанием автомобилей",
            "• Визуальный календарь бронирований (диаграмма Ганта)",
            "• Система уведомлений о возвратах автомобилей",
            "• Журнал аудита всех действий пользователей",
            "• Резервное копирование базы данных (ручное и автоматическое)",
            "• Поддержка светлой и тёмной тем оформления",
            "• Настраиваемый размер шрифта",
            "• Автоматическая загрузка фотографий автомобилей",
            "• Валидация паспортных данных и телефонов",
            "• Хеширование паролей с солью (SHA-256)",
        ]

        for feature in features_desktop:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #475569;")
            features_layout.addWidget(lbl)

        # Подзаголовок: Веб-портал
        sub2 = QLabel("🌐 Веб-портал (DriveControl):")
        sub2.setStyleSheet("font-size: 14px; font-weight: bold; color: #059669; margin-top: 10px;")
        features_layout.addWidget(sub2)

        features_web = [
            "• Онлайн-регистрация клиентов с паспортными данными",
            "• Персональные профили пользователей с редактированием",
            "• Каталог автомобилей с фотографиями и характеристиками",
            "• Онлайн-бронирование автомобилей с расчётом стоимости",
            "• Система обращений в поддержку с перепиской",
            "• Запросы на возврат автомобилей с подтверждением админа",
            "• Админ-панель для управления пользователями и автопарком",
            "• Статистика и отчёты для администраторов",
            "• Система уведомлений в реальном времени",
            "• Загрузка и просмотр прикреплённых файлов",
            "• Консоль разработчика с мониторингом логов",
        ]

        for feature in features_web:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #475569;")
            features_layout.addWidget(lbl)

        # Подзаголовок: Общие возможности
        sub3 = QLabel("🔧 Общие возможности:")
        sub3.setStyleSheet("font-size: 14px; font-weight: bold; color: #059669; margin-top: 10px;")
        features_layout.addWidget(sub3)

        features_common = [
            "• Синхронизация фото между СУ и веб-порталом",
            "• Консоль разработчика с мониторингом в реальном времени",
            "• Централизованная система логирования (app.log, web_portal.log, audit.log)",
            "• Индивидуальные уведомления для каждого пользователя",
            "• Автоматическая проверка просроченных возвратов",
            "• Экспорт логов и очистка старых записей",
            "• Миграция базы данных с Alembic",
        ]

        for feature in features_common:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #475569;")
            features_layout.addWidget(lbl)

        layout.addWidget(features_group)
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    # ========================================================================
    # ВКЛАДКА 2: ВЕБ-ПОРТАЛ (НОВАЯ)
    # ========================================================================
    def _create_web_portal_tab(self) -> QWidget:
        """Вкладка «Веб-портал DriveControl»."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("🌐 Веб-портал DriveControl")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2563EB; padding: 10px 0;")
        layout.addWidget(title)

        intro = QLabel(
            "DriveControl — это веб-интерфейс системы, доступный через браузер. "
            "Предназначен для клиентов (онлайн-бронирование, профиль, обращения) "
            "и администраторов (управление пользователями, автопарком, заявками)."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("font-size: 13px; color: #475569; padding: 10px 0;")
        layout.addWidget(intro)

        # Технические детали
        tech_frame = QFrame()
        tech_frame.setObjectName("web_tech_frame")
        tech_frame.setStyleSheet("""
            QFrame#web_tech_frame {
                background-color: #EFF6FF;
                border: 2px solid #3B82F6;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        tech_layout = QVBoxLayout(tech_frame)

        tech_title = QLabel("⚙️ Технические характеристики")
        tech_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E40AF;")
        tech_layout.addWidget(tech_title)

        tech_items = [
            ("Фреймворк:", "FastAPI 0.137.1 (асинхронный)"),
            ("ASGI-сервер:", "Uvicorn 0.49.0"),
            ("Адрес запуска:", "http://127.0.0.1:8000"),
            ("Админ-панель:", "http://127.0.0.1:8000/admin"),
            ("Управление автопарком:", "http://127.0.0.1:8000/admin/cars"),
            ("Правила и договоры:", "http://127.0.0.1:8000/rules"),
            ("Скрытая ссылка с логами для разработчика:", "http://127.0.0.1:8000/dev-logs"),
            ("База данных:", "Общая с десктопной СУ (rental.db)"),
            ("Статические файлы:", "/static/car_images/, /static/support_attachments/"),
        ]

        for label, value in tech_items:
            tech_layout.addWidget(self._make_info_row(label, value))

        layout.addWidget(tech_frame)

        # Функции для клиентов
        client_frame = QFrame()
        client_frame.setObjectName("client_frame")
        client_frame.setStyleSheet("""
            QFrame#client_frame {
                background-color: #D1FAE5;
                border: 2px solid #10B981;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        client_layout = QVBoxLayout(client_frame)

        client_title = QLabel("👤 Функции для клиентов")
        client_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #065F46;")
        client_layout.addWidget(client_title)

        client_features = [
            "• Регистрация с валидацией паспортных данных",
            "• Персональный профиль с редактированием (телефон, email, адрес, дата рождения)",
            "• Каталог автомобилей с фильтрацией и фотографиями",
            "• Детальная страница каждого автомобиля с характеристиками",
            "• Онлайн-бронирование с автоматическим расчётом стоимости",
            "• Скидки: 10% при аренде от 7 дней, 20% от 14 дней",
            "• Просмотр своих активных и завершённых аренд",
            "• Система обращений в поддержку с историей переписки",
            "• Запросы на возврат автомобилей с подтверждением админом",
            "• Прикрепление файлов к обращениям (изображения, PDF, DOC)",
            "• Система уведомлений в реальном времени",
            "• Просмотр правил и условий аренды",
        ]

        for feature in client_features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #064E3B;")
            client_layout.addWidget(lbl)

        layout.addWidget(client_frame)

        # Функции для админов
        admin_frame = QFrame()
        admin_frame.setObjectName("admin_frame")
        admin_frame.setStyleSheet("""
            QFrame#admin_frame {
                background-color: #FEE2E2;
                border: 2px solid #EF4444;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        admin_layout = QVBoxLayout(admin_frame)

        admin_title = QLabel("🔧 Функции для администраторов")
        admin_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #991B1B;")
        admin_layout.addWidget(admin_title)

        admin_features = [
            "• Управление пользователями (CRUD, смена ролей, блокировка)",
            "• Изменение логинов и паролей пользователей",
            "• Просмотр детальной информации о каждом пользователе с историей аренд",
            "• Управление автопарком (добавление, редактирование, удаление)",
            "• Загрузка фотографий автомобилей (PNG, JPG, JPEG, WEBP)",
            "• Изменение статуса автомобилей (доступен / на ТО)",
            "• Управление запросами на возврат (подтверждение / отклонение)",
            "• Ответы на обращения в поддержку",
            "• Закрытие обращений как решённых",
            "• Статистика и отчёты (выручка, популярные авто, доход за месяц)",
            "• Управление техническим обслуживанием",
            "• Просмотр всех платежей и штрафов",
            "• Синхронизация фото с десктопной СУ",
        ]

        for feature in admin_features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #7F1D1D;")
            admin_layout.addWidget(lbl)

        layout.addWidget(admin_frame)

        # Безопасность
        security_frame = QFrame()
        security_frame.setObjectName("security_frame")
        security_frame.setStyleSheet("""
            QFrame#security_frame {
                background-color: #FEF3C7;
                border: 2px solid #F59E0B;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        security_layout = QVBoxLayout(security_frame)

        security_title = QLabel("🔒 Безопасность веб-портала")
        security_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #92400E;")
        security_layout.addWidget(security_title)

        security_features = [
            "• Хеширование паролей SHA-256 с индивидуальной солью",
            "• Сессии через HTTP-only cookies (защита от XSS)",
            "• Проверка прав доступа на каждом endpoint",
            "• Защита от несанкционированного доступа к админ-панели",
            "• Валидация всех входных данных (Form, Query, Path)",
            "• Логирование всех попыток входа (успешных и неудачных)",
            "• Автоматическое создание клиента при первом входе пользователя",
        ]

        for feature in security_features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #78350F;")
            security_layout.addWidget(lbl)

        layout.addWidget(security_frame)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    # ========================================================================
    # ВКЛАДКА 3: СИСТЕМА ПОДДЕРЖКИ (НОВАЯ)
    # ========================================================================
    def _create_support_system_tab(self) -> QWidget:
        """Вкладка «Система обращений в поддержку»."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("💬 Система обращений в поддержку")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #2563EB; padding: 10px 0;")
        layout.addWidget(title)

        intro = QLabel(
            "Система поддержки обеспечивает двустороннюю коммуникацию между клиентами "
            "и администрацией. Клиенты могут создавать обращения, прикреплять файлы, "
            "получать ответы и продолжать диалог. Администраторы видят все обращения "
            "в единой панели и могут отвечать через веб-портал или десктопную СУ."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("font-size: 13px; color: #475569; padding: 10px 0;")
        layout.addWidget(intro)

        # Жизненный цикл обращения
        lifecycle_frame = QFrame()
        lifecycle_frame.setObjectName("lifecycle_frame")
        lifecycle_frame.setStyleSheet("""
            QFrame#lifecycle_frame {
                background-color: #DBEAFE;
                border: 2px solid #3B82F6;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        lifecycle_layout = QVBoxLayout(lifecycle_frame)

        lifecycle_title = QLabel("🔄 Жизненный цикл обращения")
        lifecycle_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E40AF;")
        lifecycle_layout.addWidget(lifecycle_title)

        lifecycle_items = [
            ("1️⃣ PENDING (Ожидает):", "Клиент создал обращение, ждёт ответа админа"),
            ("2️⃣ IN_PROGRESS (В работе):", "Админ ответил или клиент продолжил обращение"),
            ("3️⃣ RESOLVED (Решено):", "Админ закрыл обращение как решённое"),
            ("4️⃣ Продолжение:", "Клиент может возобновить решённое обращение"),
        ]

        for label, value in lifecycle_items:
            lifecycle_layout.addWidget(self._make_info_row(label, value))

        layout.addWidget(lifecycle_frame)

        # Функции для клиента
        client_frame = QFrame()
        client_frame.setStyleSheet("""
            QFrame {
                background-color: #D1FAE5;
                border: 2px solid #10B981;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        client_layout = QVBoxLayout(client_frame)

        client_title = QLabel("👤 Возможности клиента")
        client_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #065F46;")
        client_layout.addWidget(client_title)

        client_features = [
            "• Создание обращений с указанием темы и описания",
            "• Прикрепление файлов (изображения, PDF, DOC) до 5 МБ",
            "• Просмотр истории всех своих обращений",
            "• Детальный просмотр каждого обращения с ответами",
            "• Продолжение решённых обращений с доп. информацией",
            "• Получение уведомлений об ответах админов",
            "• Просмотр прикреплённых файлов с возможностью скачивания",
        ]

        for feature in client_features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #064E3B;")
            client_layout.addWidget(lbl)

        layout.addWidget(client_frame)

        # Функции для админа
        admin_frame = QFrame()
        admin_frame.setStyleSheet("""
            QFrame {
                background-color: #FEE2E2;
                border: 2px solid #EF4444;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        admin_layout = QVBoxLayout(admin_frame)

        admin_title = QLabel("🔧 Возможности администратора")
        admin_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #991B1B;")
        admin_layout.addWidget(admin_title)

        admin_features = [
            "• Просмотр списка всех обращений с фильтрацией по статусу",
            "• Детальный просмотр каждого обращения",
            "• Ответ на обращение через форму (сохраняется в истории)",
            "• Закрытие обращения как решённого",
            "• Отправка сообщений клиенту через десктопную СУ",
            "• Просмотр прикреплённых файлов клиентов",
            "• Получение уведомлений о новых и продолженных обращениях",
            "• Открытие профиля клиента из уведомления",
        ]

        for feature in admin_features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #7F1D1D;")
            admin_layout.addWidget(lbl)

        layout.addWidget(admin_frame)

        # Технические детали
        tech_frame = QFrame()
        tech_frame.setStyleSheet("""
            QFrame {
                background-color: #FEF3C7;
                border: 2px solid #F59E0B;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        tech_layout = QVBoxLayout(tech_frame)

        tech_title = QLabel("⚙️ Технические детали")
        tech_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #92400E;")
        tech_layout.addWidget(tech_title)

        tech_items = [
            ("Модель:", "SupportRequest (SQLAlchemy)"),
            ("Статусы:", "Enum SupportRequestStatus (PENDING, IN_PROGRESS, RESOLVED)"),
            ("Сообщения:", "SupportMessage — история переписки"),
            ("Прикреплённые файлы:", "Папка /static/support_attachments/"),
            ("Уведомления:", "Создаются автоматически при создании/продолжении обращения"),
            ("Индивидуальное прочтение:", "Таблица notification_reads (каждый админ видит свои)"),
            ("Макс. размер файла:", "5 МБ на файл"),
            ("Поддерживаемые форматы:", "JPG, PNG, GIF, WEBP, PDF, DOC, DOCX, TXT"),
        ]

        for label, value in tech_items:
            tech_layout.addWidget(self._make_info_row(label, value))

        layout.addWidget(tech_frame)

        # Система уведомлений
        notif_frame = QFrame()
        notif_frame.setStyleSheet("""
            QFrame {
                background-color: #EDE9FE;
                border: 2px solid #8B5CF6;
                border-radius: 10px;
                padding: 15px;
                margin: 5px 0;
            }
        """)
        notif_layout = QVBoxLayout(notif_frame)

        notif_title = QLabel("🔔 Система уведомлений")
        notif_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #5B21B6;")
        notif_layout.addWidget(notif_title)

        notif_features = [
            "• Автоматическое создание уведомлений при новых обращениях",
            "• Уведомления о продолжении обращений клиентами",
            "• Уведомления об ответах админов (для клиентов)",
            "• Уведомления о закрытии обращений (для клиентов)",
            "• Индивидуальное прочтение для админов (таблица notification_reads)",
            "• Автоматическая проверка каждые 5 минут в десктопной СУ",
            "• Цветовая индикация приоритетов (critical, high, medium)",
            "• Быстрый переход к обращению из уведомления",
        ]

        for feature in notif_features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #4C1D95;")
            notif_layout.addWidget(lbl)

        layout.addWidget(notif_frame)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    # ========================================================================
    # ========================================================================
    def _create_permissions_tab(self) -> QWidget:
        """Вкладка «Роли и права» с подробным описанием."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel("🔐 Система ролей и прав доступа")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563EB; padding: 10px 0;")
        layout.addWidget(title_label)

        intro_text = QLabel(
            "В системе реализована многоуровневая система прав доступа (RBAC). "
            "Каждая роль имеет определённый набор прав, которые можно индивидуально настраивать."
        )
        intro_text.setWordWrap(True)
        intro_text.setStyleSheet("font-size: 13px; color: #475569; padding: 10px 0;")
        layout.addWidget(intro_text)

        # Описание ролей
        roles_info = [
            {
                "title": "👑 Главный Администратор (superadmin)",
                "color": "#DC2626",
                "bg_color": "#FEE2E2",
                "description": "Неизменяемая роль с максимальными привилегиями. Не может быть удалена или деактивирована.",
                "rights": [
                    "✓ Полный доступ ко всем разделам системы",
                    "✓ Создание/редактирование/удаление любых пользователей (кроме себя)",
                    "✓ Назначение любых прав и ролей",
                    "✓ Управление базой данных (создание, удаление, восстановление)",
                    "✓ Просмотр журнала аудита всех действий",
                    "✓ Доступ к настройкам системы",
                    "✓ Экспорт любых отчётов",
                    "✓ Доступ к консоли разработчика",
                    "⚠️ Нельзя изменить свои данные или деактивировать себя",
                ]
            },
            {
                "title": "🔧 Администратор (admin)",
                "color": "#2563EB",
                "bg_color": "#DBEAFE",
                "description": "Полный доступ ко всем функциям системы с некоторыми ограничениями.",
                "rights": [
                    "✓ Полный доступ ко всем разделам (кроме управления супер-админом)",
                    "✓ Создание/редактирование/удаление пользователей (кроме superadmin)",
                    "✓ Назначение ролей и прав (кроме роли superadmin)",
                    "✓ Управление резервным копированием",
                    "✓ Просмотр журнала аудита",
                    "✓ Доступ к настройкам приложения",
                    "✓ Экспорт отчётов и статистики",
                    "✓ Доступ к консоли разработчика",
                    "✗ НЕ может удалять или редактировать superadmin",
                    "✗ НЕ может назначать роль superadmin",
                ]
            },
            {
                "title": "👨‍💼 Менеджер (manager)",
                "color": "#059669",
                "bg_color": "#D1FAE5",
                "description": "Управление основными бизнес-процессами: клиентами, автомобилями, договорами.",
                "rights": [
                    "✓ Просмотр дашборда и статистики",
                    "✓ Полный CRUD для автомобилей, клиентов, договоров",
                    "✓ Управление штрафами и ТО",
                    "✓ Экспорт договоров и отчётов",
                    "✓ Просмотр календаря бронирований",
                    "✗ НЕ имеет доступа к журналу аудита",
                    "✗ НЕ может управлять пользователями",
                    "✗ НЕ имеет доступа к настройкам БД",
                    "✗ НЕ может создавать резервные копии",
                    "✗ НЕ имеет доступа к консоли разработчика",
                ]
            },
            {
                "title": "👤 Оператор (operator)",
                "color": "#7C3AED",
                "bg_color": "#EDE9FE",
                "description": "Минимальные права для оформления договоров и просмотра информации.",
                "rights": [
                    "✓ Просмотр дашборда",
                    "✓ Просмотр автопарка, клиентов, договоров",
                    "✓ Создание новых договоров аренды",
                    "✓ Просмотр уведомлений",
                    "✓ Смена собственного пароля",
                    "✗ НЕ может создавать/редактировать автомобили",
                    "✗ НЕ может создавать/редактировать клиентов",
                    "✗ НЕ имеет доступа к статистике и отчётам",
                    "✗ НЕ может управлять штрафами и ТО (только просмотр)",
                    "✗ НЕ имеет доступа к настройкам",
                ]
            }
        ]

        for role in roles_info:
            role_frame = QFrame()
            role_frame.setObjectName("role_frame")
            role_frame.setStyleSheet(f"""
                QFrame#role_frame {{
                    background-color: {role['bg_color']};
                    border: 2px solid {role['color']};
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px 0;
                }}
            """)
            role_layout = QVBoxLayout(role_frame)
            role_layout.setSpacing(8)

            role_title = QLabel(role["title"])
            role_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {role['color']};")
            role_layout.addWidget(role_title)

            role_desc = QLabel(role["description"])
            role_desc.setWordWrap(True)
            role_desc.setStyleSheet("font-size: 13px; color: #1E293B; font-style: italic;")
            role_layout.addWidget(role_desc)

            rights_label = QLabel("Права доступа:")
            rights_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #1E293B; margin-top: 8px;")
            role_layout.addWidget(rights_label)

            for right in role["rights"]:
                right_label = QLabel(right)
                right_label.setWordWrap(True)
                right_label.setStyleSheet("font-size: 12px; color: #1E293B; padding-left: 10px;")
                role_layout.addWidget(right_label)

            layout.addWidget(role_frame)

        # Таблица прав
        table_title = QLabel("\n📋 Сводная таблица прав доступа")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563EB; padding: 15px 0 10px 0;")
        layout.addWidget(table_title)

        table = QTableWidget()
        table.setObjectName("permissions_table")
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Право", "SuperAdmin", "Admin", "Manager", "Operator"])

        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setWordWrap(True)

        permissions_data = [
            ("Просмотр дашборда", "✓", "✓", "✓", "✓"),
            ("Управление автопарком (CRUD)", "✓", "✓", "✓", "✗"),
            ("Управление клиентами (CRUD)", "✓", "✓", "✓", "✗"),
            ("Создание договоров", "✓", "✓", "✓", "✓"),
            ("Редактирование договоров", "✓", "✓", "✓", "✗"),
            ("Управление штрафами", "✓", "✓", "✓", "✗"),
            ("Управление ТО", "✓", "✓", "✓", "✗"),
            ("Просмотр статистики", "✓", "✓", "✓", "✗"),
            ("Экспорт отчётов", "✓", "✓", "✓", "✗"),
            ("Журнал аудита", "✓", "✓", "✗", "✗"),
            ("Резервное копирование БД", "✓", "✓", "✗", "✗"),
            ("Управление пользователями", "✓", "✓", "✗", "✗"),
            ("Настройки приложения", "✓", "✓", "✓", "✗"),
            ("Консоль разработчика", "✓", "✓", "✗", "✗"),
            ("Смена пароля", "✓", "✓", "✓", "✓"),
        ]

        table.setRowCount(len(permissions_data))
        for row, (permission, superadmin, admin, manager, operator) in enumerate(permissions_data):
            table.setItem(row, 0, QTableWidgetItem(permission))
            table.setItem(row, 1, QTableWidgetItem(superadmin))
            table.setItem(row, 2, QTableWidgetItem(admin))
            table.setItem(row, 3, QTableWidgetItem(manager))
            table.setItem(row, 4, QTableWidgetItem(operator))

            # Цветовое оформление
            for col in range(1, 5):
                item = table.item(row, col)
                if item.text() == "✓":
                    item.setForeground(Qt.GlobalColor.darkGreen)
                else:
                    item.setForeground(Qt.GlobalColor.red)

        table.setStyleSheet("""
            QTableWidget#permissions_table {
                background-color: #FFFFFF;
                alternate-background-color: #F8FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 10px;
                gridline-color: #E2E8F0;
                font-size: 13px;
            }
            QTableWidget#permissions_table::item {
                padding: 10px;
                border-bottom: 1px solid #E2E8F0;
            }
            QTableWidget#permissions_table::item:selected {
                background-color: #DBEAFE;
                color: #1E3A8A;
            }
            QHeaderView::section {
                background-color: #F1F5F9;
                color: #1E293B;
                font-weight: bold;
                padding: 14px;
                border: none;
                border-bottom: 3px solid #CBD5E1;
                font-size: 13px;
            }
        """)

        layout.addWidget(table)

        # Легенда
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        legend_layout = QHBoxLayout(legend_frame)

        legend_layout.addWidget(QLabel("✓ — Право доступно"))
        legend_layout.addWidget(QLabel("✗ — Право недоступно"))
        legend_layout.addStretch()

        layout.addWidget(legend_frame)
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    # ========================================================================
    # ВКЛАДКА 5: ИНСТРУКЦИЯ (РАСШИРЕННАЯ)
    # ========================================================================
    def _create_instruction_tab(self) -> QWidget:
        """Вкладка с инструкцией по каждой вкладке приложения."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        intro_label = QLabel(
            "📖 Инструкция по работе с системой AutoRent Pro\n\n"
            "Добро пожаловать в информационную систему управления арендой автомобилей!\n"
            "Ниже приведено краткое описание каждой вкладки интерфейса."
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("font-size: 14px; font-weight: bold; padding-bottom: 10px;")
        layout.addWidget(intro_label)

        # Описание вкладок (РАСШИРЕННОЕ)
        sections = [
            ("📊 Дашборд",
             "Главная панель управления. Отображает ключевые показатели:\n"
             "• Общее количество автомобилей в автопарке\n"
             "• Количество активных договоров аренды\n"
             "• Общее число зарегистрированных клиентов\n"
             "• Выручка за текущий месяц\n\n"
             "🔄 АВТООБНОВЛЕНИЕ:\n"
             "Дашборд автоматически обновляется каждые 30 секунд.\n"
             "Это позволяет видеть актуальные данные без необходимости\n"
             "переключаться между вкладками.\n\n"
             "💡 Индикатор в правом верхнем углу показывает время\n"
             "последнего обновления и частоту автообновления.\n\n"
             "Используйте дашборд для быстрой оценки состояния бизнеса."),

            ("🚗 Автопарк",
             "Управление автопарком компании.\n\n"
             "Функции:\n"
             "• Просмотр списка всех автомобилей с характеристиками\n"
             "• Поиск по марке, модели или гос. номеру\n"
             "• Добавление нового автомобиля (кнопка «➕ Добавить»)\n"
             "• Редактирование данных автомобиля (кнопка «✏️ Редактировать»)\n"
             "• Удаление автомобиля из автопарка\n"
             "• Двойной клик по строке — просмотр детальной карточки с фотографией\n\n"
             "💡 Совет: Загрузите фото автомобиля в папку /images с именем, "
             "совпадающим с гос. номером (например, А777АА777.jpg), "
             "и оно подгрузится автоматически. Фото синхронизируются с веб-порталом."),

            ("👥 Клиенты",
             "Управление базой клиентов.\n\n"
             "Функции:\n"
             "• Просмотр списка клиентов с паспортными данными\n"
             "• Поиск по ФИО\n"
             "• Добавление нового клиента\n"
             "• Удаление клиента из базы\n\n"
             "⚠️ При добавлении клиента проверяется уникальность телефона и email.\n"
             "📝 Паспортные данные включают: серию, номер, дату и место выдачи."),

            ("📝 Договоры",
             "Оформление и управление договорами аренды.\n\n"
             "Функции:\n"
             "• Создание нового договора аренды (выбор клиента, авто, дат)\n"
             "• Автоматический расчёт стоимости на основе ставки авто\n"
             "• Скидки: 10% при аренде от 7 дней, 20% от 14 дней\n"
             "• Завершение активного договора (автомобиль возвращается в доступные)\n"
             "• Экспорт договоров в PDF (одним файлом или отдельными)\n"
             "• Поиск по клиенту или автомобилю\n\n"
             "💡 Используйте Ctrl+клик или Shift+клик для выбора нескольких договоров "
             "для массового экспорта в PDF."),

            ("⚠️ Штрафы",
             "Учёт штрафов и повреждений автомобилей.\n\n"
             "Функции:\n"
             "• Добавление штрафа к активному договору\n"
             "• Отметка штрафа как оплаченного\n"
             "• Отмена штрафа\n"
             "• Удаление записи о штрафе\n"
             "• Карточки статистики: всего штрафов, не оплачено, оплачено\n\n"
             "Типы штрафов: повреждение, просрочка возврата, курение, мойка и др."),

            ("🔧 ТО",
             "Управление техническим обслуживанием автомобилей.\n\n"
             "Функции:\n"
             "• Добавление записи о ТО (плановое, сезонное, внеплановое)\n"
             "• Указание пробега, стоимости, исполнителя\n"
             "• Автоматическое планирование следующего ТО\n"
             "• Отметка ТО как выполненного\n"
             "• Отмена или удаление записи ТО\n"
             "• Карточки статистики: всего записей, запланировано, выполнено"),

            ("🔔 Уведомления",
             "Система уведомлений о возвратах, обращениях и запросах.\n\n"
             "Функции:\n"
             "• Автоматическая проверка каждые 5 минут\n"
             "• Уведомления о предстоящих возвратах (за 1-3 дня)\n"
             "• Уведомления о просроченных возвратах\n"
             "• Уведомления о новых обращениях в поддержку\n"
             "• Уведомления о запросах на возврат автомобилей\n"
             "• Цветовая индикация приоритета (критический, высокий, средний)\n"
             "• Отметка уведомлений как прочитанных\n"
             "• Быстрый переход к договору/обращению по клику\n"
             "• Кнопка «Написать пользователю» для ответа клиенту\n\n"
             "💡 Уведомления индивидуальны для каждого пользователя.\n"
             "🔒 Админы видят общие уведомления с индивидуальным прочтением."),

            ("📅 Календарь",
             "Визуальное представление бронирований в виде диаграммы Ганта.\n\n"
             "Функции:\n"
             "• Выбор периода отображения\n"
             "• Цветовое кодирование: синий — активный договор, зелёный — завершён\n"
             "• Отображение записей ТО (жёлтый — запланировано, зелёный — выполнено)\n"
             "• Наведение на полосу — всплывающая подсказка с деталями\n"
             "• Клик по полосе — открытие полной информации"),

            ("📈 Статистика",
             "Аналитика и статистика по бизнесу.\n\n"
             "Разделы:\n"
             "• Учёт расходов и ремонтов (таблица с фильтрацией)\n"
             "• Топ-5 популярных автомобилей по количеству аренд и доходу\n"
             "• Добавление новых расходов (ремонт, страховка, прочее)\n\n"
             "💡 Сортировка топа: сначала по количеству аренд, затем по доходу."),

            ("📑 Отчёты",
             "Экспорт данных в формате CSV.\n\n"
             "Функции:\n"
             "• Экспорт реестра договоров аренды\n"
             "• Экспорт финансовой статистики за период:\n"
             "  — Общие доходы и расходы\n"
             "  — Чистая прибыль\n"
             "  — Топ-10 автомобилей по доходности\n"
             "  — Расходы по типам\n\n"
             "📄 Файлы сохраняются в кодировке UTF-8 с BOM для корректного "
             "отображения кириллицы в MS Excel."),

            ("🛡️ Безопасность",
             "Журнал аудита и управление базой данных.\n\n"
             "Функции:\n"
             "• Просмотр журнала всех действий пользователей\n"
             "• Создание резервной копии БД\n"
             "• Создание пустой БД (только структура таблиц)\n"
             "• Создание БД с тестовыми данными\n"
             "• Восстановление БД из резервной копии\n"
             "• Удаление БД (с двойным подтверждением)\n\n"
             "⚠️ Операции с БД необратимы. Рекомендуется создать резервную копию."),

            ("⚙️ Настройки",
             "Настройки приложения.\n\n"
             "Разделы:\n"
             "• Размер шрифта (10-20pt)\n"
             "• Тип базы данных (SQLite/PostgreSQL)\n"
             "• Путь для резервных копий\n"
             "• Автоматическое резервное копирование:\n"
             "  — Частота (ежечасно, ежедневно, еженедельно, ежемесячно)\n"
             "  — Время выполнения\n"
             "  — Максимальное количество бэкапов\n"
             "• Email-уведомления\n"
             "• Информация о приложении\n\n"
             "💡 Тема оформления переключается кнопкой в левой панели."),

            ("👤 Пользователи",
             "Управление учётными записями (только для администраторов).\n\n"
             "Функции:\n"
             "• Просмотр списка всех пользователей\n"
             "• Поиск по логину или ФИО\n"
             "• Создание нового пользователя\n"
             "• Редактирование данных пользователя\n"
             "• Назначение роли (SuperAdmin, Admin, Manager, Operator)\n"
             "• Индивидуальная настройка прав доступа\n"
             "• Деактивация/активация учётной записи\n"
             "• Удаление пользователя\n"
             "• Смена логина и пароля пользователя\n\n"
             "⚠️ Главный Администратор (superadmin) не может быть изменён обычным админом."),

            ("🐞 Консоль разработчика",
             "Расширенная консоль для мониторинга и отладки (только для админов).\n\n"
             "Вкладки:\n"
             "• 🌐 Веб-портал — логи FastAPI-сервера\n"
             "• 💻 СУ (Desktop) — логи десктопного приложения\n"
             "• 👥 Пользователи — последние активные пользователи\n"
             "• 🗄️ База данных — статистика БД в реальном времени\n"
             "• ⚙️ Система — информация о CPU, RAM, диске\n\n"
             "Функции:\n"
             "• Автообновление каждые 3 секунды\n"
             "• Фильтрация по уровню (DEBUG, INFO, WARNING, ERROR)\n"
             "• Экспорт логов в текстовый файл\n"
             "• Очистка логов\n\n"
             "💡 Логи хранятся в папке /logs/ с ротацией."),

            ("ℹ️ О программе",
             "Информация о системе, инструкция, роли и контакты.\n\n"
             "Открывается по клику на последний пункт меню.\n"
             "Содержит подробное описание всех функций системы, "
             "технологического стека и архитектуры."),
        ]

        # Подзаголовок: Веб-портал
        web_title = QLabel("\n🌐 ВЕБ-ПОРТАЛ DRIVECONTROL")
        web_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563EB; padding: 15px 0 10px 0;")
        layout.addWidget(web_title)

        web_intro = QLabel(
            "Веб-портал доступен по адресу http://127.0.0.1:8000\n"
            "Ниже приведено описание основных разделов веб-интерфейса."
        )
        web_intro.setWordWrap(True)
        web_intro.setStyleSheet("font-size: 13px; color: #475569; padding-bottom: 10px;")
        layout.addWidget(web_intro)

        web_sections = [
            ("🏠 Главная страница",
             "• Каталог автомобилей с фотографиями\n"
             "• Список активных и завершённых аренд (для клиента)\n"
             "• Статистика (для админа): выручка, активные аренды, загрузка автопарка\n"
             "• Система уведомлений с счётчиком непрочитанных\n"
             "• Быстрый доступ к профилю и выходу"),

            ("🔐 Вход и регистрация",
             "• Вход по логину и паролю\n"
             "• Регистрация с валидацией:\n"
             "  — Фамилия, имя, отчество\n"
             "  — Паспортные данные (серия, номер, дата и место выдачи)\n"
             "  — Телефон (проверка уникальности)\n"
             "  — Email (проверка уникальности)\n"
             "  — Логин и пароль\n"
             "• Автоматическое создание клиента при первом входе"),

            ("👤 Профиль клиента",
             "• Просмотр и редактирование персональных данных:\n"
             "  — Телефон, email, адрес\n"
             "  — Дата рождения\n"
             "  — Паспортные данные\n"
             "• История обращений в поддержку\n"
             "• Список активных и завершённых аренд"),

            ("🚗 Страница автомобиля",
             "• Подробная информация об автомобиле:\n"
             "  — Марка, модель, год выпуска\n"
             "  — Тип кузова, цвет, количество мест\n"
             "  — КПП, тип топлива\n"
             "  — Объём и мощность двигателя\n"
             "  — Гос. номер, суточная ставка\n"
             "  — Описание и фотография\n"
             "• Статус: доступен / в аренде / на ТО\n"
             "• Кнопка бронирования (для клиентов)"),

            ("📩 Обращения в поддержку",
             "• Создание нового обращения с темой и описанием\n"
             "• Прикрепление файлов (изображения, PDF, DOC) до 5 МБ\n"
             "• Просмотр истории всех обращений\n"
             "• Детальный просмотр с ответами админов\n"
             "• Продолжение решённых обращений\n"
             "• Статусы: Ожидает → В работе → Решено"),

            ("🔄 Запросы на возврат",
             "• Клиент создаёт запрос на возврат автомобиля\n"
             "• Админ получает уведомление в СУ\n"
             "• Админ подтверждает или отклоняет запрос\n"
             "• При подтверждении аренда завершается автоматически\n"
             "• Автомобиль возвращается в доступные"),

            ("🔧 Админ-панель",
             "Доступна по адресу /admin:\n"
             "• Управление пользователями (CRUD, смена ролей)\n"
             "• Управление автопарком (/admin/cars)\n"
             "• Загрузка фотографий автомобилей\n"
             "• Управление запросами на возврат (/admin/return-requests)\n"
             "• Управление обращениями в поддержку (/admin/support-requests)\n"
             "• Детальный просмотр профилей пользователей"),
        ]

        for title, description in sections + web_sections:
            group = QFrame()
            group.setObjectName("instruction_section")
            group.setStyleSheet("""
                QFrame#instruction_section {
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 5px 0;
                }
            """)
            group_layout = QVBoxLayout(group)
            group_layout.setSpacing(5)

            section_title = QLabel(title)
            section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563EB;")
            group_layout.addWidget(section_title)

            section_text = QLabel(description)
            section_text.setWordWrap(True)
            section_text.setStyleSheet("font-size: 13px; color: #475569; line-height: 1.5;")
            group_layout.addWidget(section_text)

            layout.addWidget(group)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    # ========================================================================
    # ВКЛАДКА 6: КОНТАКТЫ (ОБНОВЛЁННАЯ)
    # ========================================================================
    def _create_contacts_tab(self) -> QWidget:
        """Вкладка «Контакты»."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Контактная информация
        contacts_group = QFrame()
        contacts_group.setObjectName("about_info_group")
        contacts_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #F8FAFC;
            }
        """)
        contacts_layout = QVBoxLayout(contacts_group)
        contacts_layout.setSpacing(15)

        contacts_title = QLabel("✉️ Контактная информация")
        contacts_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563EB;")
        contacts_layout.addWidget(contacts_title)

        contacts_layout.addWidget(self._make_info_row("Разработчики:", "Студенты МТУСИ"))
        contacts_layout.addWidget(
            self._make_info_row("Университет:", "Московский технический университет связи и информатики (МТУСИ)"))
        contacts_layout.addWidget(self._make_info_row("Кафедра:", "«Программная инженерия»"))
        contacts_layout.addWidget(self._make_info_row("Email:", "bogdan.coolline25@gmail.com"))
        contacts_layout.addWidget(self._make_info_row("GitHub:", "https://github.com/Xynary25/MTUCI-Car-Rental"))

        layout.addWidget(contacts_group)

        # Адреса веб-портала
        urls_group = QFrame()
        urls_group.setObjectName("about_info_group")
        urls_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #EFF6FF;
            }
        """)
        urls_layout = QVBoxLayout(urls_group)
        urls_layout.setSpacing(10)

        urls_title = QLabel("🌐 Адреса веб-портала DriveControl")
        urls_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E40AF;")
        urls_layout.addWidget(urls_title)

        urls_layout.addWidget(self._make_info_row("Главная:", "http://127.0.0.1:8000"))
        urls_layout.addWidget(self._make_info_row("Админ-панель:", "http://127.0.0.1:8000/admin"))
        urls_layout.addWidget(self._make_info_row("Управление автопарком:", "http://127.0.0.1:8000/admin/cars"))
        urls_layout.addWidget(
            self._make_info_row("Обращения в поддержку:", "http://127.0.0.1:8000/admin/support-requests"))
        urls_layout.addWidget(self._make_info_row("Запросы на возврат:", "http://127.0.0.1:8000/admin/return-requests"))
        urls_layout.addWidget(self._make_info_row("Правила и договоры:", "http://127.0.0.1:8000/rules"))
        urls_layout.addWidget(
            self._make_info_row("Скрытая ссылка с логами для разработчика:", "http://127.0.0.1:8000/admin/dev-logs"))

        layout.addWidget(urls_group)

        # Лицензия
        license_group = QFrame()
        license_group.setObjectName("about_info_group")
        license_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #F8FAFC;
            }
        """)
        license_layout = QVBoxLayout(license_group)
        license_layout.setSpacing(10)

        license_title = QLabel("📄 Лицензия и использование")
        license_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2563EB;")
        license_layout.addWidget(license_title)

        license_text = QLabel(
            "Данное программное обеспечение разработано в рамках учебной практики "
            "по направлению 09.03.01 «Информатика и вычислительная техника».\n\n"
            "Система состоит из двух компонентов:\n"
            "• AutoRent Pro — десктопная СУ на PyQt6 для сотрудников\n"
            "• DriveControl — веб-портал на FastAPI для клиентов и администраторов\n\n"
            "Оба приложения работают с общей базой данных SQLite (rental.db), "
            "что обеспечивает синхронизацию данных в реальном времени.\n\n"
            "Все данные хранятся локально в базе данных SQLite. "
            "Для многопользовательского режима рекомендуется миграция на PostgreSQL.\n\n"
            "© 2026 AutoRent Pro. Все права защищены."
        )
        license_text.setWordWrap(True)
        license_text.setStyleSheet("font-size: 13px; color: #475569; line-height: 1.6;")
        license_layout.addWidget(license_text)

        layout.addWidget(license_group)

        # Тестовые аккаунты
        accounts_group = QFrame()
        accounts_group.setObjectName("about_info_group")
        accounts_group.setStyleSheet("""
            QFrame#about_info_group {
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                padding: 20px;
                background-color: #FEF3C7;
            }
        """)
        accounts_layout = QVBoxLayout(accounts_group)
        accounts_layout.setSpacing(10)

        accounts_title = QLabel("🔑 Тестовые аккаунты")
        accounts_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #92400E;")
        accounts_layout.addWidget(accounts_title)

        accounts_text = QLabel(
            "Для тестирования системы созданы следующие учётные записи:\n\n"
            "Десктопная СУ (AutoRent Pro):\n"
            "• super / superadmin123 — Главный Администратор\n"
            "• admin / admin123 — Администратор\n"
            "• manager / manager123 — Менеджер\n"
            "• operator / operator123 — Оператор\n\n"
            "Веб-портал (DriveControl):\n"
            "• Те же логины/пароли для входа в админ-панель\n"
            "• Клиенты регистрируются самостоятельно через форму регистрации\n\n"
            "⚠️ Рекомендуется сменить пароли после первого входа!"
        )
        accounts_text.setWordWrap(True)
        accounts_text.setStyleSheet("font-size: 13px; color: #78350F; line-height: 1.6;")
        accounts_layout.addWidget(accounts_text)

        layout.addWidget(accounts_group)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    # ========================================================================
    # ВСПОМОГАТЕЛЬНЫЙ МЕТОД
    # ========================================================================
    def _make_info_row(self, label: str, value: str) -> QLabel:
        """Создание строки информации."""
        text = QLabel(f"<b>{label}</b> {value}")
        text.setWordWrap(True)
        text.setStyleSheet("font-size: 13px; color: #1E293B; line-height: 1.5;")
        return text