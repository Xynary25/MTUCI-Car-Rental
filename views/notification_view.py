import webbrowser

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QFrame, QMessageBox, QMenu, QAbstractItemView, QMainWindow)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from database import SessionLocal
from models import Notification
from models.support_request import SupportRequestStatus
from utils.notification_service import NotificationService
from datetime import datetime, timedelta
from utils.signals import global_signals


class NotificationWidget(QWidget):
    """Виджет уведомлений о возвратах автомобилей."""

    def auto_check_notifications(self):
        """Автоматическая проверка уведомлений."""
        try:
            if not hasattr(self, 'db') or self.db is None:
                print("❌ База данных не инициализирована")
                return

            if not hasattr(self, 'current_user') or self.current_user is None:
                print("❌ Пользователь не авторизован")
                return

            try:
                user_id = self.current_user.id if self.current_user else None
            except Exception as e:
                print(f"❌ Пользователь не доступен: {e}")
                return

            print("🔔 Проверка уведомлений...")

            # Существующие проверки
            self.notification_service.check_upcoming_returns(days_ahead=1, user_id=user_id)
            self.notification_service.check_overdue_returns(user_id=user_id)

            # Проверка запросов на возврат
            self.check_return_requests()

            # Проверка обращений в поддержку
            self.check_support_requests()

            print("🔄 Обновление интерфейса уведомлений...")
            self.load_notifications()
            self.update_unread_count()

        except Exception as e:
            print(f"❌ Ошибка в auto_check_notifications: {e}")
            import traceback
            traceback.print_exc()

    def check_return_requests(self):
        """Проверка новых запросов на возврат (для админов)."""
        try:
            from models.return_request import ReturnRequest, ReturnRequestStatus
            from models.notification import Notification

            # Проверяем только если пользователь админ
            if not self.current_user.has_permission('view_users'):
                return

            pending_requests = self.db.query(ReturnRequest).filter(
                ReturnRequest.status == ReturnRequestStatus.PENDING
            ).all()

            for req in pending_requests:
                existing = self.db.query(Notification).filter(
                    Notification.notification_type == "return_request",
                    Notification.agreement_id == req.id,  # Используем ID запроса
                    Notification.is_read == False
                ).first()

                if not existing:
                    notification = Notification(
                        title=f"🔄 Запрос на возврат #{req.id}",
                        message=f"Клиент {req.client_name} запросил возврат автомобиля {req.car_info}",
                        notification_type="return_request",
                        priority="high",
                        agreement_id=req.id,  # Сохраняем ID запроса
                        user_id=None,  # None чтобы видели все админы
                        is_read=False
                    )
                    self.db.add(notification)
                    self.db.commit()
                    print(f"✅ Создано уведомление о возврате #{req.id}")
        except Exception as e:
            print(f"Ошибка проверки возвратов: {e}")

    def check_support_requests(self):
        """Проверка новых обращений в поддержку (для админов)."""
        try:
            from models.support_request import SupportRequest, SupportRequestStatus
            from models.notification import Notification

            # Проверяем только если пользователь админ
            if not self.current_user.has_permission('view_users'):
                return

            pending_requests = self.db.query(SupportRequest).filter(
                SupportRequest.status == SupportRequestStatus.PENDING
            ).all()

            for req in pending_requests:
                existing = self.db.query(Notification).filter(
                    Notification.notification_type == "support_request",
                    Notification.agreement_id == req.id,  # Используем ID обращения
                    Notification.is_read == False
                ).first()

                if not existing:
                    notification = Notification(
                        title=f"📩 Обращение в поддержку #{req.id}",
                        message=f"{req.client_name}: {req.subject}",
                        notification_type="support_request",
                        priority="medium",
                        agreement_id=req.id,  # Сохраняем ID обращения
                        user_id=None,  # None чтобы видели все админы
                        is_read=False
                    )
                    self.db.add(notification)
                    self.db.commit()
                    print(f"✅ Создано уведомление об обращении #{req.id}")
        except Exception as e:
            print(f"Ошибка проверки обращений: {e}")

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
        self.check_btn = QPushButton(" Проверить сейчас")
        self.check_btn.setMinimumHeight(40)
        self.check_btn.clicked.connect(self.manual_check_notifications)
        header_layout.addWidget(self.check_btn)

        self.mark_all_read_btn = QPushButton("✅ Все прочитано")
        self.mark_all_read_btn.setMinimumHeight(40)
        self.mark_all_read_btn.clicked.connect(self.mark_all_as_read)
        header_layout.addWidget(self.mark_all_read_btn)

        layout.addLayout(header_layout)

        # Счетчик непрочитанных
        self.unread_count_label = QLabel(" ")
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

        # Scroll area для уведомлений
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # разрешаем изменение размера
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setMinimumHeight(500)  # Увеличиваем минимальную высоту
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.notifications_container = QWidget()
        self.notifications_container.setMinimumWidth(600)  # минимальная ширина

        self.notifications_layout = QVBoxLayout(self.notifications_container)
        self.notifications_layout.setSpacing(10)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area.setWidget(self.notifications_container)
        layout.addWidget(self.scroll_area, 1)  # stretch=1 чтобы занимал все пространство

        # Загрузка уведомлений
        self.load_notifications()

    def manual_check_notifications(self):
        """Ручная проверка уведомлений."""
        user_id = self.current_user.id if self.current_user else None

        # Существующие проверки
        upcoming = self.notification_service.check_upcoming_returns(days_ahead=3, user_id=user_id)
        overdue = self.notification_service.check_overdue_returns(user_id=user_id)

        # Проверка запросов на возврат и обращений
        self.check_return_requests()
        self.check_support_requests()

        # Пересчитываем общее количество
        new_notifications = self.db.query(Notification).filter(
            Notification.is_read == False,
            Notification.created_at >= datetime.now() - timedelta(minutes=5)
        ).count()

        if new_notifications > 0:
            QMessageBox.information(
                self, "Проверка завершена",
                f"Найдено новых уведомлений: {new_notifications}\n\n"
                f"• Предстоящих возвратов: {len(upcoming)}\n"
                f"• Просроченных: {len(overdue)}\n"
                f"• Запросов на возврат и обращений проверено"
            )
        else:
            QMessageBox.information(
                self, "Проверка завершена",
                "Новых уведомлений нет. Все автомобили возвращаются вовремя!"
            )

        self.load_notifications()
        self.update_unread_count()

    def refresh_notifications(self):
        """Принудительное обновление уведомлений."""
        print("🔄 Обновление уведомлений...")
        self.load_notifications()
        self.update_unread_count()

    def load_notifications(self):
        """Загрузка и отображение уведомлений."""
        print(f"📥 Загрузка уведомлений для пользователя: {self.current_user}")

        # Очистка старых уведомлений
        while self.notifications_layout.count():
            child = self.notifications_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        user_id = self.current_user.id if self.current_user else None
        print(f"🔍 user_id для фильтрации: {user_id}")

        notifications = self.notification_service.get_all_notifications(user_id=user_id, limit=50)
        print(f"✅ Найдено уведомлений: {len(notifications)}")

        if not notifications:
            print("⚠️ Уведомлений нет")
            empty_label = QLabel(" Уведомлений нет")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #94A3B8;
                    padding: 40px;
                }
            """)
            self.notifications_layout.addWidget(empty_label)
            self.notifications_container.adjustSize()
            self.scroll_area.update()
            return

        for notification in notifications:
            print(f"  - {notification.title}")
            notification_card = self.create_notification_card(notification)
            # устанавливаем минимальную высоту
            notification_card.setMinimumHeight(150)
            self.notifications_layout.addWidget(notification_card)

        # НЕ добавляем addStretch() - это сжимает карточки!
        # self.notifications_layout.addStretch()

        self.notifications_layout.activate()
        self.notifications_container.adjustSize()
        self.scroll_area.update()
        self.scroll_area.repaint()

        print("✅ Все уведомления добавлены в layout")

    def create_notification_card(self, notification):
        """Создание карточки уведомления с улучшенным дизайном."""
        card = QFrame()
        card.setObjectName("notification_card")
        card.setMinimumHeight(180)
        card.setMaximumHeight(250)

        # Стиль в зависимости от типа и приоритета
        if notification.notification_type == "return_request":
            bg_color = "#FEF3C7"
            border_color = "#F59E0B"
        elif notification.notification_type == "support_request":
            bg_color = "#DBEAFE"
            border_color = "#3B82F6"
        elif notification.is_read:
            bg_color = "#F1F5F9"
            border_color = "#CBD5E1"
        else:
            if notification.priority == 'critical':
                bg_color = "#FEE2E2"
                border_color = "#EF4444"
            elif notification.priority == 'high':
                bg_color = "#FEF3C7"
                border_color = "#F59E0B"
            else:
                bg_color = "#DBEAFE"
                border_color = "#3B82F6"

        card.setStyleSheet(f"""
            QFrame#notification_card {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 15px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # Заголовок
        header_layout = QHBoxLayout()
        title_label = QLabel(notification.title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 15px;
                color: #1E293B;
            }
        """)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)

        time_label = QLabel(notification.created_at.strftime("%d.%m.%Y %H:%M"))
        time_label.setStyleSheet("color: #64748B; font-size: 12px;")
        header_layout.addWidget(time_label)

        # Проверяем, прочитано ли уведомление текущим пользователем
        from models.notification import NotificationRead
        user_id = self.current_user.id if self.current_user else None
        is_read_for_user = False

        if notification.is_read and notification.user_id == user_id:
            # Личное уведомление и оно прочитано
            is_read_for_user = True
        elif notification.user_id is None and user_id:
            # Общее уведомление - проверяем таблицу прочтений
            existing_read = self.db.query(NotificationRead).filter(
                NotificationRead.notification_id == notification.id,
                NotificationRead.user_id == user_id
            ).first()
            is_read_for_user = existing_read is not None

        if not is_read_for_user:
            unread_badge = QLabel("●")
            unread_badge.setStyleSheet("color: #EF4444; font-size: 18px; font-weight: bold;")
            header_layout.addWidget(unread_badge)

        layout.addLayout(header_layout)

        # Сообщение с прокруткой если длинное
        message_label = QLabel(notification.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #475569;
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.5);
                border-radius: 6px;
            }
        """)
        message_label.setMinimumHeight(60)
        layout.addWidget(message_label)

        # Кнопки действий
        actions_layout = QHBoxLayout()

        # Проверяем, нужно ли показывать кнопку "Отметить прочитанным"
        show_mark_read = False
        if notification.user_id == user_id and not notification.is_read:
            # Личное уведомление не прочитано
            show_mark_read = True
        elif notification.user_id is None and user_id:
            # Общее уведомление - проверяем таблицу прочтений
            existing_read = self.db.query(NotificationRead).filter(
                NotificationRead.notification_id == notification.id,
                NotificationRead.user_id == user_id
            ).first()
            if not existing_read:
                show_mark_read = True

        if show_mark_read:
            mark_read_btn = QPushButton("✓ Отметить прочитанным")
            mark_read_btn.setMinimumHeight(36)
            mark_read_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            mark_read_btn.clicked.connect(
                lambda checked, nid=notification.id: self.mark_as_read(nid)
            )
            actions_layout.addWidget(mark_read_btn)

        # Кнопка просмотра договора / обращения
        if notification.agreement_id:
            # Определяем текст кнопки в зависимости от типа
            if notification.notification_type in ["support_request", "support_message", "support_response",
                                                  "support_resolved"]:
                btn_text = "📄 Открыть обращение"
                btn_color = "#8B5CF6"
                btn_hover = "#7C3AED"
            else:
                btn_text = "📄 Открыть договор"
                btn_color = "#3B82F6"
                btn_hover = "#2563EB"

            view_agreement_btn = QPushButton(btn_text)
            view_agreement_btn.setMinimumHeight(36)
            view_agreement_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                }}
            """)
            view_agreement_btn.clicked.connect(
                lambda checked, aid=notification.agreement_id, ntype=notification.notification_type:
                self.view_agreement(aid, ntype)
            )
            actions_layout.addWidget(view_agreement_btn)

        # Кнопки для запросов на возврат
        if notification.notification_type == "return_request" and notification.agreement_id:
            approve_btn = QPushButton("✅ Подтвердить возврат")
            approve_btn.setMinimumHeight(36)
            approve_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            approve_btn.clicked.connect(
                lambda checked, nid=notification.id: self.approve_return_request(nid)
            )
            actions_layout.addWidget(approve_btn)

            reject_btn = QPushButton("❌ Отклонить")
            reject_btn.setMinimumHeight(36)
            reject_btn.setStyleSheet("""
                QPushButton {
                    background-color: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            """)
            reject_btn.clicked.connect(
                lambda checked, nid=notification.id: self.reject_return_request(nid)
            )
            actions_layout.addWidget(reject_btn)

        # Кнопки для обращений в поддержку (ОРИГИНАЛЬНОЕ + ПРОДОЛЖЕННОЕ)
        if notification.notification_type in ["support_request", "support_message", "support_response",
                                              "support_resolved"]:
            if notification.agreement_id:  # agreement_id содержит ID обращения
                # Кнопка просмотра деталей обращения
                view_details_btn = QPushButton("📄 Открыть детали обращения")
                view_details_btn.setMinimumHeight(32)
                view_details_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #15dce5;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1afdff;
                    }
                """)
                view_details_btn.clicked.connect(
                    lambda checked, rid=notification.agreement_id: self.show_support_request_details(rid)
                )
                actions_layout.addWidget(view_details_btn)

            # Кнопка просмотра профиля клиента
            view_profile_btn = QPushButton("👤 Профиль клиента")
            view_profile_btn.setMinimumHeight(32)
            view_profile_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2563EB;
                }
            """)
            view_profile_btn.clicked.connect(
                lambda checked, nid=notification.id: self.view_client_profile_from_notification(nid)
            )
            actions_layout.addWidget(view_profile_btn)

        # Кнопка: Написать пользователю
        send_message_btn = QPushButton("✉️ Написать пользователю")
        send_message_btn.setMinimumHeight(32)
        send_message_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B5CF6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
        """)
        send_message_btn.clicked.connect(
            lambda checked, nid=notification.id: self.send_message_to_user(nid)
        )
        actions_layout.addWidget(send_message_btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        return card

    def mark_as_read(self, notification_id: int):
        """Отметить уведомление как прочитанное для текущего пользователя."""
        user_id = self.current_user.id if self.current_user else None

        if self.notification_service.mark_as_read(notification_id, user_id):
            print(f"✅ Уведомление #{notification_id} помечено как прочитанное пользователем ID={user_id}")
            self.load_notifications()
            self.update_unread_count()
        else:
            print(f"⚠️ Не удалось пометить уведомление #{notification_id} как прочитанное")

    def mark_all_as_read(self):
        """Отметить все уведомления как прочитанные для текущего пользователя."""
        user_id = self.current_user.id if self.current_user else None
        count = self.notification_service.mark_all_as_read(user_id)
        QMessageBox.information(
            self, "Успех",
            f"Все уведомления ({count}) отмечены как прочитанные для вас"
        )
        print(f"✅ Пользователь ID={user_id} отметил {count} уведомлений как прочитанные")
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

    def view_agreement(self, agreement_id: int, notification_type: str = None):
        """Открыть договор или профиль клиента в зависимости от типа уведомления."""
        try:
            # Если это уведомление об обращении в поддержку — открываем браузер ===
            if notification_type in ["support_request", "support_message", "support_response", "support_resolved"]:
                # Ищем обращение в поддержке
                from models.support_request import SupportRequest
                support_req = self.db.query(SupportRequest).filter(
                    SupportRequest.id == agreement_id
                ).first()

                if support_req:
                    # Ищем клиента по имени
                    from models.client import Client
                    client = self.db.query(Client).filter(
                        Client.full_name == support_req.client_name
                    ).first()

                    if client:
                        # Открываем профиль клиента в браузере с гиперссылкой
                        import webbrowser
                        profile_url = f"http://127.0.0.1:8000/admin/user/{client.id}"
                        webbrowser.open(profile_url)

                        QMessageBox.information(
                            self, "Обращение открыто",
                            f"📩 Обращение #{support_req.id}\n\n"
                            f"👤 Клиент: {support_req.client_name}\n"
                            f"📋 Тема: {support_req.subject}\n\n"
                            f"Профиль клиента открыт в браузере:\n"
                            f"<a href='{profile_url}'>{profile_url}</a>"
                        )
                        return
                    else:
                        QMessageBox.warning(
                            self, "Ошибка",
                            f"Клиент '{support_req.client_name}' не найден в БД"
                        )
                        return
                else:
                    QMessageBox.warning(
                        self, "Внимание",
                        f"Обращение #{agreement_id} не найдено"
                    )
                    return

            # === СТАРЫЙ КОД: Открытие договора ===
            from PyQt6.QtWidgets import QMainWindow

            main_window = None
            parent = self.parent()

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

            main_window.content_stack.setCurrentIndex(agreement_tab_index)
            main_window.sidebar.setCurrentRow(agreement_tab_index)

            agreement_widget = main_window.content_stack.widget(agreement_tab_index)

            if not agreement_widget or not hasattr(agreement_widget, 'table'):
                QMessageBox.warning(
                    self, "Ошибка",
                    "Не удалось найти виджет договоров"
                )
                return

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

    def approve_return_request(self, notification_id: int):
        """Подтверждение запроса на возврат."""
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()

            if not notification or not notification.agreement_id:
                QMessageBox.warning(self, "Ошибка", "Уведомление не найдено")
                return

            # Открываем договор и подтверждаем возврат
            self.view_agreement(notification.agreement_id)

            QMessageBox.information(
                self, "Информация",
                "Перейдите к договору и завершите аренду для подтверждения возврата"
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обработать запрос: {str(e)}")

    def reject_return_request(self, notification_id: int):
        """Отклонение запроса на возврат."""
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()

            if not notification:
                QMessageBox.warning(self, "Ошибка", "Уведомление не найдено")
                return

            # Диалог для ввода причины отклонения
            from PyQt6.QtWidgets import QInputDialog
            reason, ok = QInputDialog.getText(
                self, "Отклонение запроса",
                "Введите причину отклонения запроса на возврат:"
            )

            if ok and reason:
                # Здесь можно добавить логику отклонения через веб-портал
                QMessageBox.information(
                    self, "Запрос отклонен",
                    f"Запрос отклонен. Причина: {reason}\n\n"
                    f"Откройте веб-портал для управления запросами: http://127.0.0.1:8000/admin/return-requests"
                )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отклонить запрос: {str(e)}")

    def view_client_profile_from_notification(self, notification_id: int):
        """Просмотр профиля клиента из уведомления об обращении."""
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()

            if not notification:
                QMessageBox.warning(self, "Ошибка", "Уведомление не найдено")
                return

            client_name = None

            # Пробуем найти из support_request
            if notification.agreement_id and notification.notification_type == "support_request":
                from models.support_request import SupportRequest
                support_req = self.db.query(SupportRequest).filter(
                    SupportRequest.id == notification.agreement_id
                ).first()

                if support_req:
                    client_name = support_req.client_name

            # Если не нашли, пробуем из сообщения
            if not client_name and notification.message:
                lines = notification.message.split('\n')
                for line in lines:
                    if line.startswith('От:'):
                        client_name = line.replace('От:', '').strip()
                        break
                    elif 'Клиент' in line:
                        # Формат: "Клиент: Иванов Иван Иванович"
                        client_name = line.split(':')[1].strip() if ':' in line else None
                        break

            if client_name:
                # Ищем клиента в БД по имени
                from models.client import Client
                client = self.db.query(Client).filter(
                    Client.full_name == client_name
                ).first()

                if client:
                    # Открываем профиль в браузере
                    import webbrowser
                    profile_url = f"http://127.0.0.1:8000/admin/user/{client.id}"
                    webbrowser.open(profile_url)

                    QMessageBox.information(
                        self, "Профиль открыт",
                        f"Профиль клиента '{client_name}' открыт в браузере.\n\n"
                        f"URL: {profile_url}"
                    )
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Клиент '{client_name}' не найден в базе данных")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось определить клиента")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть профиль: {str(e)}")
            import traceback
            traceback.print_exc()

    def send_message_to_user(self, notification_id: int):
        """Отправка сообщения пользователю от поддержки."""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QHBoxLayout, QInputDialog
            from PyQt6.QtCore import Qt

            # Сначала спрашиваем ID обращения
            request_id_text, ok = QInputDialog.getText(
                self, "Отправка сообщения",
                "Введите ID обращения:\n(Если не знаете - откройте обращение и посмотрите ID)"
            )

            if not ok or not request_id_text:
                return

            try:
                request_id = int(request_id_text)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Неверный формат ID")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("✉️ Написать пользователю")
            dialog.resize(500, 400)

            layout = QVBoxLayout(dialog)

            title_label = QLabel("📨 Сообщение от службы поддержки")
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)

            layout.addWidget(QLabel("Текст сообщения:"))
            message_edit = QTextEdit()
            message_edit.setPlaceholderText("Введите текст сообщения для пользователя...")
            message_edit.setMinimumHeight(200)
            layout.addWidget(message_edit)

            btn_layout = QHBoxLayout()
            send_btn = QPushButton("📤 Отправить")
            send_btn.setMinimumHeight(40)
            send_btn.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)

            cancel_btn = QPushButton("❌ Отмена")
            cancel_btn.setMinimumHeight(40)

            send_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)

            btn_layout.addWidget(send_btn)
            btn_layout.addWidget(cancel_btn)
            layout.addLayout(btn_layout)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                message_text = message_edit.toPlainText().strip()
                if message_text:
                    try:
                        from models.support_request import SupportRequest, SupportRequestStatus
                        from models.support_message import SupportMessage
                        from models.notification import Notification
                        from datetime import datetime

                        # Находим обращение
                        support_req = self.db.query(SupportRequest).filter(
                            SupportRequest.id == request_id
                        ).first()

                        if not support_req:
                            QMessageBox.warning(self, "Ошибка", f"Обращение #{request_id} не найдено")
                            return

                        # 1. Создаём SupportMessage (история переписки)
                        support_msg = SupportMessage(
                            support_request_id=request_id,
                            sender_type="admin",
                            sender_id=self.current_user.id if self.current_user else 0,
                            message=message_text
                        )
                        self.db.add(support_msg)

                        # 2. Добавляем сообщение в description обращения
                        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
                        support_req.description += f"\n\n[Ответ поддержки {timestamp}]:\n{message_text}"

                        support_req.status = SupportRequestStatus.IN_PROGRESS
                        support_req.updated_at = datetime.utcnow()

                        # 4. Создаём уведомление для КОНКРЕТНОГО пользователя
                        notification = Notification(
                            title="📨 Ответ от поддержки",
                            message=f"По вашему обращению #{request_id}:\n{message_text[:200]}",
                            notification_type="support_message",
                            priority="medium",
                            user_id=support_req.client_id,  # ✅ Конкретный пользователь!
                            agreement_id=request_id,
                            is_read=False
                        )
                        self.db.add(notification)

                        self.db.commit()

                        QMessageBox.information(
                            self, "Успех",
                            f"Сообщение отправлено пользователю {support_req.client_name}\n"
                            f"Обращение #{request_id}"
                        )

                        self.load_notifications()

                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Не удалось отправить сообщение:\n{str(e)}")
                        import traceback
                        traceback.print_exc()
                        self.db.rollback()
                else:
                    QMessageBox.warning(self, "Внимание", "Введите текст сообщения")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отправить сообщение:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def show_support_request_details(self, request_id: int):
        """Показать детальную информацию об обращении с файлами."""
        try:
            from models.support_request import SupportRequest
            from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton,
                                         QTextEdit, QHBoxLayout, QScrollArea, QFrame,
                                         QMessageBox)
            from PyQt6.QtCore import Qt
            import webbrowser
            from pathlib import Path

            support_req = self.db.query(SupportRequest).filter(
                SupportRequest.id == request_id
            ).first()

            if not support_req:
                QMessageBox.warning(self, "Ошибка", "Обращение не найдено")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle(f"Обращение #{support_req.id}")
            dialog.resize(700, 500)

            layout = QVBoxLayout(dialog)
            layout.setSpacing(10)  # Уменьшили отступы
            layout.setContentsMargins(15, 15, 15, 15)

            # Заголовок
            title_label = QLabel(f"📩 Обращение #{support_req.id}")
            title_label.setStyleSheet("""
                font-size: 14px; 
                font-weight: bold; 
                color: #1e293b;
                margin-bottom: 10px;
            """)
            layout.addWidget(title_label)

            # Информация - больше места для описания
            info_text = QTextEdit()
            info_text.setReadOnly(True)
            info_text.setMaximumHeight(250)  # Увеличили место для описания
            info_text.setMinimumHeight(150)
            info_text.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #1e293b;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 13px;
                }
            """)
            info_text.setHtml(f"""
            <h3 style="color: #3b82f6; margin-bottom: 10px;">Информация об обращении</h3>
            <p><strong>Клиент:</strong> {support_req.client_name}</p>
            <p><strong>Тема:</strong> {support_req.subject}</p>
            <p><strong>Статус:</strong> {support_req.status.value}</p>
            <p><strong>Дата создания:</strong> {support_req.created_at.strftime('%d.%m.%Y %H:%M')}</p>
            <hr style="margin: 15px 0;">
            <p><strong>Описание:</strong></p>
            <div style="background-color: #f1f5f9; padding: 10px; border-radius: 5px; white-space: pre-wrap;">
            {support_req.description}
            </div>
            """)
            layout.addWidget(info_text)

            # Поиск и отображение прикрепленных файлов
            if '[Прикреплен файл]:' in support_req.description:
                files_label = QLabel("📎 Прикрепленные файлы:")
                files_label.setStyleSheet("""
                    font-size: 16px;
                    font-weight: bold;
                    color: #1e293b;
                    margin-top: 15px;
                    margin-bottom: 10px;
                """)
                layout.addWidget(files_label)

                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setMaximumHeight(200)

                files_widget = QWidget()
                files_layout = QVBoxLayout(files_widget)
                files_layout.setSpacing(10)

                for line in support_req.description.split('\n'):
                    if '[Прикреплен файл]:' in line:
                        file_path = line.split('[Прикреплен файл]:')[1].strip()
                        file_name = file_path.split('/')[-1]

                        file_frame = QFrame()
                        file_frame.setStyleSheet("""
                            QFrame {
                                background-color: #f8fafc;
                                border: 1px solid #e2e8f0;
                                border-radius: 8px;
                                padding: 10px;
                            }
                        """)

                        file_layout = QHBoxLayout(file_frame)

                        icon_label = QLabel()
                        if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            icon_label.setText("🖼️")
                        elif file_name.lower().endswith('.pdf'):
                            icon_label.setText("📄")
                        else:
                            icon_label.setText("📎")
                        icon_label.setStyleSheet("font-size: 24px;")
                        file_layout.addWidget(icon_label)

                        name_label = QLabel(
                            f"<b>{file_name}</b><br><span style='color: #64748b; font-size: 11px;'>{file_path}</span>")
                        name_label.setStyleSheet("color: #1e293b;")
                        file_layout.addWidget(name_label, 1)

                        open_btn = QPushButton("📂 Открыть")
                        open_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #3b82f6;
                                color: white;
                                border: none;
                                border-radius: 6px;
                                padding: 6px 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #2563eb;
                            }
                        """)
                        open_btn.clicked.connect(lambda checked, path=file_path: self.open_file(path))
                        file_layout.addWidget(open_btn)

                        files_layout.addWidget(file_frame)

                files_layout.addStretch()
                scroll.setWidget(files_widget)
                layout.addWidget(scroll)

            # Ответ админа
            if support_req.admin_response:
                response_text = QTextEdit()
                response_text.setReadOnly(True)
                response_text.setMaximumHeight(100)
                response_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #e0e7ff;
                        color: #1e293b;
                        padding: 10px;
                        border-radius: 5px;
                        font-size: 13px;
                        border-left: 4px solid #4338ca;
                    }
                """)
                response_text.setHtml(f"""
                <h3 style="color: #4338ca; margin-bottom: 10px;">📨 Ответ поддержки:</h3>
                <div style="white-space: pre-wrap;">{support_req.admin_response}</div>
                """)
                layout.addWidget(response_text)

            # Кнопки
            btn_layout = QHBoxLayout()
            close_btn = QPushButton("Закрыть")
            close_btn.setMinimumHeight(40)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            close_btn.clicked.connect(dialog.accept)
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            layout.addLayout(btn_layout)

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть обращение: {str(e)}")
            import traceback
            traceback.print_exc()

    def open_file(self, file_path: str):
        from pathlib import Path
        """Открыть файл в браузере или проводнике."""
        try:
            # Если это относительный путь, делаем его абсолютным
            if file_path.startswith('/'):
                full_path = Path(__file__).parent.parent / file_path[1:]  # Убираем начальный /
            else:
                full_path = Path(file_path)

            if full_path.exists():
                webbrowser.open(f'file://{full_path}')
            else:
                # Пробуем открыть как URL
                webbrowser.open(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")

    def closeEvent(self, event):
        self.check_timer.stop()
        self.db.close()
        super().closeEvent(event)