from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QFrame, QMessageBox, QMenu, QAbstractItemView, QMainWindow)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from database import SessionLocal
from utils.notification_service import NotificationService
from datetime import datetime
from utils.signals import global_signals


class NotificationWidget(QWidget):
    """Виджет уведомлений о возвратах автомобилей."""

    def auto_check_notifications(self):
        """Автоматическая проверка уведомлений."""
        try:
            # Проверяем что сессия жива
            if not hasattr(self, 'db') or self.db is None:
                return

            # Проверяем что пользователь ещё авторизован
            if not hasattr(self, 'current_user') or self.current_user is None:
                return

            # Проверяем что сессия не закрыта
            try:
                user_id = self.current_user.id if self.current_user else None
            except Exception as e:
                print(f"Пользователь не доступен: {e}")
                return

            self.notification_service.check_upcoming_returns(days_ahead=1, user_id=user_id)
            self.notification_service.check_overdue_returns(user_id=user_id)
            self.load_notifications()
            self.update_unread_count()
        except Exception as e:
            print(f"Ошибка в auto_check_notifications: {e}")

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.notification_service = NotificationService(self.db)
        self.current_user = current_user  # Получаем текущего пользователя

        # Таймер для периодической проверки уведомлений (каждые 5 минут)
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.auto_check_notifications)
        self.check_timer.start(300000)  # 5 минут

        # Первая проверка при запуске
        QTimer.singleShot(1000, self.auto_check_notifications)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel("🔔 Уведомления о возвратах")
        title_label.setObjectName("section_header")
        header_layout.addWidget(title_label)

        # Кнопки управления
        self.check_btn = QPushButton("🔄 Проверить сейчас")
        self.check_btn.setMinimumHeight(40)
        self.check_btn.clicked.connect(self.manual_check_notifications)
        header_layout.addWidget(self.check_btn)

        self.mark_all_read_btn = QPushButton("✅ Все прочитано")
        self.mark_all_read_btn.setMinimumHeight(40)
        self.mark_all_read_btn.clicked.connect(self.mark_all_as_read)
        header_layout.addWidget(self.mark_all_read_btn)

        layout.addLayout(header_layout)

        # Счетчик непрочитанных
        self.unread_count_label = QLabel("")
        self.unread_count_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #EF4444;
                padding: 8px;
                background-color: #FEE2E2;
                border-radius: 6px;
            }
        """)
        self.update_unread_count()
        layout.addWidget(self.unread_count_label)

        # Scroll area для уведомлений - ИСПРАВЛЕНИЕ
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setMinimumHeight(400)  # Добавляем минимальную высоту
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.notifications_container = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_container)
        self.notifications_layout.setSpacing(10)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area.setWidget(self.notifications_container)
        layout.addWidget(self.scroll_area, 1)  # Добавляем stretch=1 чтобы занимал все доступное пространство

        # Загрузка уведомлений
        self.load_notifications()

    def auto_check_notifications(self):
        """Автоматическая проверка уведомлений."""
        user_id = self.current_user.id if self.current_user else None
        self.notification_service.check_upcoming_returns(days_ahead=1, user_id=user_id)
        self.notification_service.check_overdue_returns(user_id=user_id)
        self.load_notifications()
        self.update_unread_count()

    def manual_check_notifications(self):
        """Ручная проверка уведомлений."""
        user_id = self.current_user.id if self.current_user else None
        upcoming = self.notification_service.check_upcoming_returns(days_ahead=3, user_id=user_id)
        overdue = self.notification_service.check_overdue_returns(user_id=user_id)

        total = len(upcoming) + len(overdue)
        if total > 0:
            QMessageBox.information(
                self, "Проверка завершена",
                f"Найдено новых уведомлений: {total}\n"
                f"• Предстоящих возвратов: {len(upcoming)}\n"
                f"• Просроченных: {len(overdue)}"
            )
        else:
            QMessageBox.information(
                self, "Проверка завершена",
                "Новых уведомлений нет. Все автомобили возвращаются вовремя!"
            )

        self.load_notifications()
        self.update_unread_count()

    def load_notifications(self):
        """Загрузка и отображение уведомлений."""
        # Очистка старых уведомлений
        while self.notifications_layout.count():
            child = self.notifications_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        user_id = self.current_user.id if self.current_user else None
        notifications = self.notification_service.get_all_notifications(user_id=user_id, limit=50)

        if not notifications:
            empty_label = QLabel("📭 Уведомлений нет")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #94A3B8;
                    padding: 40px;
                }
            """)
            self.notifications_layout.addWidget(empty_label)
            return

        for notification in notifications:
            notification_card = self.create_notification_card(notification)
            self.notifications_layout.addWidget(notification_card)

        self.notifications_layout.addStretch()

    def create_notification_card(self, notification):
        """Создание карточки уведомления."""
        card = QFrame()
        card.setObjectName("notification_card")

        # Стиль в зависимости от приоритета и статуса прочтения
        if notification.is_read:
            bg_color = "#F1F5F9" if notification.priority != 'critical' else "#FEE2E2"
            border_color = "#CBD5E1"
        else:
            if notification.priority == 'critical':
                bg_color = "#FEE2E2"
                border_color = "#EF4444"
            elif notification.priority == 'high':
                bg_color = "#FEF3C7"
                border_color = "#F59E0B"
            elif notification.priority == 'medium':
                bg_color = "#DBEAFE"
                border_color = "#3B82F6"
            else:
                bg_color = "#F1F5F9"
                border_color = "#94A3B8"

        card.setStyleSheet(f"""
            QFrame#notification_card {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # Заголовок и время
        header_layout = QHBoxLayout()

        title_label = QLabel(notification.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-weight: bold;
                font-size: 14px;
                color: {'#DC2626' if notification.priority == 'critical' else '#1E293B'};
            }}
        """)
        header_layout.addWidget(title_label)

        time_label = QLabel(notification.created_at.strftime("%d.%m.%Y %H:%M"))
        time_label.setStyleSheet("color: #64748B; font-size: 12px;")
        header_layout.addWidget(time_label)

        if not notification.is_read:
            unread_badge = QLabel("●")
            unread_badge.setStyleSheet("color: #EF4444; font-size: 16px;")
            header_layout.addWidget(unread_badge)

        layout.addLayout(header_layout)

        # Сообщение
        message_label = QLabel(notification.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #475569;
                padding: 5px 0;
            }
        """)
        layout.addWidget(message_label)

        # Кнопки действий
        actions_layout = QHBoxLayout()

        if not notification.is_read:
            mark_read_btn = QPushButton("✓ Отметить прочитанным")
            mark_read_btn.setMinimumHeight(32)
            mark_read_btn.clicked.connect(
                lambda checked, nid=notification.id: self.mark_as_read(nid)
            )
            actions_layout.addWidget(mark_read_btn)

        # Кнопка просмотра договора (если есть)
        if notification.agreement_id:
            view_agreement_btn = QPushButton("📄 Открыть договор")
            view_agreement_btn.setMinimumHeight(32)
            view_agreement_btn.clicked.connect(
                lambda checked, aid=notification.agreement_id: self.view_agreement(aid)
            )
            actions_layout.addWidget(view_agreement_btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        return card

    def mark_as_read(self, notification_id: int):
        """Отметить уведомление как прочитанное."""
        user_id = self.current_user.id if self.current_user else None
        if self.notification_service.mark_as_read(notification_id, user_id):
            self.load_notifications()
            self.update_unread_count()

    def mark_all_as_read(self):
        """Отметить все уведомления как прочитанные."""
        user_id = self.current_user.id if self.current_user else None
        count = self.notification_service.mark_all_as_read(user_id)
        QMessageBox.information(
            self, "Успех",
            f"Все уведомления ({count}) отмечены как прочитанные"
        )
        self.load_notifications()
        self.update_unread_count()

    def update_unread_count(self):
        """Обновить счетчик непрочитанных уведомлений."""
        user_id = self.current_user.id if self.current_user else None
        count = self.notification_service.get_unread_count(user_id)
        if count > 0:
            self.unread_count_label.setText(f"🔴 Непрочитанных: {count}")
            self.unread_count_label.setVisible(True)
        else:
            self.unread_count_label.setVisible(False)

    def view_agreement(self, agreement_id: int):
        """Открыть договор в разделе 'Договоры'."""
        try:
            # Ищем главное окно (MainWindow) в иерархии виджетов
            from PyQt6.QtWidgets import QMainWindow

            main_window = None
            parent = self.parent()

            # Поднимаемся вверх по иерархии пока не найдем MainWindow
            while parent:
                if isinstance(parent, QMainWindow):
                    main_window = parent
                    break
                parent = parent.parent()

            if not main_window:
                QMessageBox.warning(
                    self, "Ошибка",
                    "Не удалось найти главное окно приложения"
                )
                return

            # Проверяем что у главного окна есть нужные атрибуты
            if not hasattr(main_window, 'content_stack') or not hasattr(main_window, 'sidebar'):
                QMessageBox.warning(
                    self, "Ошибка",
                    "Главное окно не имеет необходимой структуры"
                )
                return

            # Находим индекс вкладки "Договоры"
            agreement_tab_index = -1
            for i in range(main_window.sidebar.count()):
                item_text = main_window.sidebar.item(i).text()
                if "Договор" in item_text or "📝" in item_text:
                    agreement_tab_index = i
                    break

            if agreement_tab_index == -1:
                QMessageBox.warning(
                    self, "Ошибка",
                    "Не найдена вкладка 'Договоры'"
                )
                return

            # Переключаемся на вкладку договоров
            main_window.content_stack.setCurrentIndex(agreement_tab_index)
            main_window.sidebar.setCurrentRow(agreement_tab_index)

            # Находим AgreementWidget
            agreement_widget = main_window.content_stack.widget(agreement_tab_index)

            if not agreement_widget or not hasattr(agreement_widget, 'table'):
                QMessageBox.warning(
                    self, "Ошибка",
                    "Не удалось найти виджет договоров"
                )
                return

            # Ждем немного чтобы таблица обновилась
            from PyQt6.QtCore import QTimer

            def highlight_and_show():
                # Ищем договор в таблице
                found = False
                for row in range(agreement_widget.table.rowCount()):
                    item = agreement_widget.table.item(row, 0)
                    if item and int(item.text()) == agreement_id:
                        # Выделяем строку
                        agreement_widget.table.selectRow(row)
                        # Прокручиваем к строке
                        agreement_widget.table.scrollToItem(
                            agreement_widget.table.item(row, 0),
                            QAbstractItemView.ScrollHint.PositionAtCenter
                        )

                        # Показываем информацию
                        agreement_data = None
                        if hasattr(agreement_widget, 'all_agreements'):
                            agreement_data = next(
                                (a for a in agreement_widget.all_agreements if a["id"] == agreement_id),
                                None
                            )

                        info_text = f"Договор #{agreement_id}"
                        if agreement_data:
                            info_text += (
                                f"\n\nКлиент: {agreement_data['client_name']}\n"
                                f"Автомобиль: {agreement_data['car_info']}\n"
                                f"Период: {agreement_data['start_date']} - {agreement_data['end_date']}\n"
                                f"Стоимость: {agreement_data['total_cost']} руб.\n"
                                f"Статус: {agreement_data['status']}"
                            )

                        QMessageBox.information(self, "Договор найден", info_text)
                        found = True
                        break

                if not found:
                    QMessageBox.warning(
                        self, "Внимание",
                        f"Договор #{agreement_id} не найден в таблице"
                    )

            # Запускаем поиск с небольшой задержкой
            QTimer.singleShot(100, highlight_and_show)

        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось открыть договор:\n{str(e)}"
            )

    def closeEvent(self, event):
        self.check_timer.stop()
        self.db.close()
        super().closeEvent(event)