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

        # Вкладка 1: О системе
        self.tabs.addTab(self._create_about_tab(), "ℹ️ О системе")

        # Вкладка 2: Роли и права (таблица)
        self.tabs.addTab(self._create_permissions_tab(), "🔐 Роли и права")

        # Вкладка 3: Инструкция
        self.tabs.addTab(self._create_instruction_tab(), "📖 Инструкция")

        # Вкладка 4: Контакты
        self.tabs.addTab(self._create_contacts_tab(), "✉️ Контакты")

        layout.addWidget(self.tabs, stretch=1)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(45)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _create_about_tab(self) -> QWidget:
        """Вкладка «О системе»."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Основная информация
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

        info_layout.addWidget(self._make_info_row("Название:", "AutoRent Pro"))
        info_layout.addWidget(self._make_info_row("Версия:", "1.0.0"))
        info_layout.addWidget(self._make_info_row(
            "Описание:",
            "Информационная система управления арендой легковых автомобилей. "
            "Автоматизирует процессы учёта автопарка, клиентов, договоров аренды, "
            "финансового учёта и отчётности."
        ))
        info_layout.addWidget(self._make_info_row("Разработчик:", "Студент МТУСИ, кафедра «Программная инженерия»"))
        info_layout.addWidget(self._make_info_row("Год разработки:", "2026"))
        info_layout.addWidget(self._make_info_row("Учебная практика:", "Технологическая практика МТУСИ"))

        layout.addWidget(info_group)

        # Технологический стек
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
            ("Графический интерфейс:", "PyQt6 (фреймворк Qt6)"),
            ("ORM:", "SQLAlchemy 2.0"),
            ("База данных:", "SQLite (по умолчанию), PostgreSQL (опционально)"),
            ("Генерация PDF:", "ReportLab"),
            ("Планировщик задач:", "APScheduler"),
            ("Архитектура:", "MVC (Model-View-Controller)"),
            ("Система безопасности:", "RBAC (Role-Based Access Control)"),
        ]

        for label, value in tech_items:
            tech_layout.addWidget(self._make_info_row(label, value))

        layout.addWidget(tech_group)

        # Реализованный функционал
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

        features = [
            "• Полный CRUD для автомобилей, клиентов, договоров",
            "• Система ролей и прав доступа (SuperAdmin, Admin, Manager, Operator)",
            "• Индивидуальная настройка прав для каждого пользователя",
            "• Автоматический расчёт стоимости аренды",
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

        for feature in features:
            lbl = QLabel(feature)
            lbl.setStyleSheet("font-size: 13px; color: #475569;")
            features_layout.addWidget(lbl)

        layout.addWidget(features_group)
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

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
                    "⚠️ Нельзя изменить свои данные или деактивировать себя"
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
                    "✗ НЕ может удалять или редактировать superadmin",
                    "✗ НЕ может назначать роль superadmin"
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
                    "✗ НЕ может создавать резервные копии"
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
                    "✗ НЕ имеет доступа к настройкам"
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
            ("Резервное копирование БД", "✓", "✓", "✗", ""),
            ("Управление пользователями", "✓", "✓", "✗", "✗"),
            ("Настройки приложения", "✓", "✓", "✓", "✗"),
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

        # Описание вкладок
        sections = [
            ("📊 Дашборд",
             "Главная панель управления. Отображает ключевые показатели:\n"
             "• Общее количество автомобилей в автопарке\n"
             "• Количество активных договоров аренды\n"
             "• Общее число зарегистрированных клиентов\n"
             "• Выручка за текущий месяц\n\n"
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
             "и оно подгрузится автоматически."),

            ("👥 Клиенты",
             "Управление базой клиентов.\n\n"
             "Функции:\n"
             "• Просмотр списка клиентов с паспортными данными\n"
             "• Поиск по ФИО\n"
             "• Добавление нового клиента\n"
             "• Удаление клиента из базы\n\n"
             "⚠️ При добавлении клиента проверяется уникальность телефона и email."),

            ("📝 Договоры",
             "Оформление и управление договорами аренды.\n\n"
             "Функции:\n"
             "• Создание нового договора аренды (выбор клиента, авто, дат)\n"
             "• Автоматический расчёт стоимости на основе ставки авто\n"
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
             "Система уведомлений о возвратах автомобилей.\n\n"
             "Функции:\n"
             "• Автоматическая проверка каждые 5 минут\n"
             "• Уведомления о предстоящих возвратах (за 1-3 дня)\n"
             "• Уведомления о просроченных возвратах\n"
             "• Цветовая индикация приоритета (критический, высокий, средний)\n"
             "• Отметка уведомлений как прочитанных\n"
             "• Быстрый переход к договору по клику\n\n"
             "💡 Уведомления индивидуальны для каждого пользователя."),

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
             "• Назначение роли (Администратор, Менеджер, Оператор)\n"
             "• Индивидуальная настройка прав доступа\n"
             "• Деактивация/активация учётной записи\n"
             "• Удаление пользователя\n\n"
             "⚠️ Главный Администратор (superadmin) не может быть изменён обычным админом."),

            ("ℹ️ О программе",
             "Информация о системе, инструкция, роли и контакты.\n\n"
             "Открывается по клику на последний пункт меню.")
        ]

        for title, description in sections:
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

    def _create_contacts_tab(self) -> QWidget:
        """Вкладка «Контакты»."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

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

        contacts_layout.addWidget(self._make_info_row("Разработчик:", "Студент МТУСИ"))
        contacts_layout.addWidget(
            self._make_info_row("Университет:", "Московский технический университет связи и информатики (МТУСИ)"))
        contacts_layout.addWidget(self._make_info_row("Кафедра:", "«Программная инженерия»"))
        contacts_layout.addWidget(self._make_info_row("Email:", "bogdan.coolline25@gmail.com"))
        contacts_layout.addWidget(self._make_info_row("GitHub:", "https://github.com/Xynary25/MTUCI-Car-Rental"))

        layout.addWidget(contacts_group)

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
            "Система предназначена для использования в качестве реального сервиса "
            "для пункта проката автомобилей.\n\n"
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
            "• superadmin / superadmin123 — Главный Администратор\n"
            "• admin / admin123 — Администратор\n"
            "• manager / manager123 — Менеджер\n"
            "• operator / operator123 — Оператор\n\n"
            "⚠️ Рекомендуется сменить пароли после первого входа!"
        )
        accounts_text.setWordWrap(True)
        accounts_text.setStyleSheet("font-size: 13px; color: #78350F; line-height: 1.6;")
        accounts_layout.addWidget(accounts_text)

        layout.addWidget(accounts_group)
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _make_info_row(self, label: str, value: str) -> QLabel:
        """Создание строки информации."""
        text = QLabel(f"<b>{label}</b> {value}")
        text.setWordWrap(True)
        text.setStyleSheet("font-size: 13px; color: #1E293B; line-height: 1.5;")
        return text