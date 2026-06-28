from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from models.notification import Notification
from models.agreement import RentalAgreement, AgreementStatus
from models.car import Car
from models.client import Client
import logging
from models.return_request import ReturnRequest, ReturnRequestStatus
from models.support_request import SupportRequest, SupportRequestStatus

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис управления уведомлениями о возвратах автомобилей."""

    def __init__(self, db_session: Session):
        """Инициализация сервиса уведомлений."""
        self.db = db_session

        # ✅ Проверяем и создаём таблицу notification_reads если её нет
        try:
            from models.notification import NotificationRead
            from sqlalchemy import inspect

            inspector = inspect(self.db.bind)
            if 'notification_reads' not in inspector.get_table_names():
                print("🔧 Создание таблицы notification_reads...")
                NotificationRead.__table__.create(self.db.bind)
                print("✅ Таблица notification_reads создана!")
        except Exception as e:
            print(f"⚠️ Не удалось создать таблицу notification_reads: {e}")

    def check_upcoming_returns(self, days_ahead: int = 1, user_id: int = None) -> list:
        """
        Проверка автомобилей, которые должны быть возвращены в ближайшие days_ahead дней.
        Возвращает список созданных уведомлений.
        """
        notifications = []
        today = date.today()
        future_date = today + timedelta(days=days_ahead)

        # Находим активные договоры, которые заканчиваются в ближайшие days_ahead дней
        upcoming_agreements = self.db.query(RentalAgreement).filter(
            RentalAgreement.status == AgreementStatus.ACTIVE,
            RentalAgreement.end_date >= today,
            RentalAgreement.end_date <= future_date
        ).all()

        for agreement in upcoming_agreements:
            # Проверяем, не создавали ли уже уведомление сегодня ДЛЯ ЭТОГО ПОЛЬЗОВАТЕЛЯ
            existing_notification = self.db.query(Notification).filter(
                Notification.agreement_id == agreement.id,
                Notification.notification_type == 'return_soon',
                Notification.user_id == user_id,
                Notification.created_at >= datetime.now() - timedelta(days=1)
            ).first()

            if not existing_notification:
                days_left = (agreement.end_date - today).days

                if days_left == 0:
                    priority = 'critical'
                    title = "🔴 СРОЧНО: Автомобиль должен быть возвращен СЕГОДНЯ"
                    message = (f"Автомобиль {agreement.car.brand} {agreement.car.model} "
                               f"({agreement.car.license_plate}) должен быть возвращен сегодня!\n"
                               f"Клиент: {agreement.client.full_name}\n"
                               f"Телефон: {agreement.client.phone}")
                elif days_left == 1:
                    priority = 'high'
                    title = "🟡 Автомобиль должен быть возвращен завтра"
                    message = (f"Автомобиль {agreement.car.brand} {agreement.car.model} "
                               f"({agreement.car.license_plate}) должен быть возвращен завтра.\n"
                               f"Клиент: {agreement.client.full_name}\n"
                               f"Телефон: {agreement.client.phone}")
                else:
                    priority = 'medium'
                    title = f"⚪ Автомобиль должен быть возвращен через {days_left} дн."
                    message = (f"Автомобиль {agreement.car.brand} {agreement.car.model} "
                               f"({agreement.car.license_plate}) должен быть возвращен "
                               f"через {days_left} дн. ({agreement.end_date.strftime('%d.%m.%Y')}).\n"
                               f"Клиент: {agreement.client.full_name}")

                notification = Notification(
                    title=title,
                    message=message,
                    notification_type='return_soon',
                    priority=priority,
                    agreement_id=agreement.id,
                    car_id=agreement.car_id,
                    user_id=user_id
                )
                self.db.add(notification)
                notifications.append(notification)
                logger.info(f"Создано уведомление о возврате: {title}")

        self.db.commit()
        return notifications

    def check_overdue_returns(self, user_id: int = None) -> list:
        """
        Проверка просроченных возвратов автомобилей.
        Возвращает список созданных уведомлений.
        """
        notifications = []
        today = date.today()

        # Находим активные договоры с истекшей датой возврата
        overdue_agreements = self.db.query(RentalAgreement).filter(
            RentalAgreement.status == AgreementStatus.ACTIVE,
            RentalAgreement.end_date < today
        ).all()

        for agreement in overdue_agreements:
            # Проверяем, не создавали ли уже уведомление сегодня ДЛЯ ЭТОГО ПОЛЬЗОВАТЕЛЯ
            existing_notification = self.db.query(Notification).filter(
                Notification.agreement_id == agreement.id,
                Notification.notification_type == 'overdue',
                Notification.user_id == user_id,
                Notification.created_at >= datetime.now() - timedelta(days=1)
            ).first()

            if not existing_notification:
                days_overdue = (today - agreement.end_date).days

                if days_overdue == 1:
                    priority = 'high'
                    title = "🟡 Автомобиль просрочен на 1 день"
                else:
                    priority = 'critical'
                    title = f"🔴 Автомобиль просрочен на {days_overdue} дн."

                message = (f"Автомобиль {agreement.car.brand} {agreement.car.model} "
                           f"({agreement.car.license_plate}) просрочен на {days_overdue} дн.!\n"
                           f"Клиент: {agreement.client.full_name}\n"
                           f"Телефон: {agreement.client.phone}\n"
                           f"Дата возврата: {agreement.end_date.strftime('%d.%m.%Y')}")

                notification = Notification(
                    title=title,
                    message=message,
                    notification_type='overdue',
                    priority=priority,
                    agreement_id=agreement.id,
                    car_id=agreement.car_id,
                    user_id=user_id
                )
                self.db.add(notification)
                notifications.append(notification)
                logger.warning(f"Создано уведомление о просрочке: {title}")

        self.db.commit()
        return notifications

    def get_unread_count(self, user_id: int = None) -> int:
        """Получить количество непрочитанных уведомлений пользователя."""
        from models.notification import NotificationRead
        from sqlalchemy import and_, or_

        if user_id is None:
            # Старая логика для обратной совместимости
            return self.db.query(Notification).filter(
                Notification.is_read == False
            ).count()

        # Получаем ID уведомлений, которые пользователь уже прочитал
        read_notification_ids = set(
            r.notification_id for r in self.db.query(NotificationRead).filter(
                NotificationRead.user_id == user_id
            ).all()
        )

        # Считаем непрочитанные
        query = self.db.query(Notification).filter(
            or_(
                # Личные уведомления, которые ещё не прочитаны
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                ),
                # Общие уведомления, которые этот пользователь ещё не прочитал
                and_(
                    Notification.user_id == None,
                    ~Notification.id.in_(read_notification_ids) if read_notification_ids else True
                )
            )
        )

        return query.count()

    def get_unread_notifications(self, user_id: int = None, limit: int = 50) -> list:
        """Получение непрочитанных уведомлений для конкретного пользователя."""
        from models.notification import NotificationRead
        from sqlalchemy import and_, or_

        if user_id is None:
            # Старая логика для обратной совместимости
            return self.db.query(Notification).filter(
                Notification.is_read == False
            ).order_by(Notification.created_at.desc()).limit(limit).all()

        # Получаем ID уведомлений, которые пользователь уже прочитал
        read_notification_ids = [
            r.notification_id for r in self.db.query(NotificationRead).filter(
                NotificationRead.user_id == user_id
            ).all()
        ]

        # Получаем уведомления:
        # 1. Личные для этого пользователя (user_id == user_id) - которые ещё не прочитаны
        # 2. Общие (user_id == None) - которые этот пользователь ещё не прочитал
        query = self.db.query(Notification).filter(
            or_(
                # Личные уведомления, которые ещё не прочитаны (is_read=False)
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                ),
                # Общие уведомления, которые этот пользователь ещё не прочитал
                and_(
                    Notification.user_id == None,
                    ~Notification.id.in_(read_notification_ids) if read_notification_ids else True
                )
            )
        )

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_all_notifications(self, user_id: int = None, limit: int = 100) -> list:
        """Получение всех уведомлений для конкретного пользователя."""
        if user_id is None:
            # Старая логика для обратной совместимости
            return self.db.query(Notification).order_by(
                Notification.created_at.desc()
            ).limit(limit).all()

        # Получаем все уведомления для пользователя (личные + общие)
        return self.db.query(Notification).filter(
            (Notification.user_id == user_id) | (Notification.user_id == None)
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id: int, user_id: int = None) -> bool:
        """Отметить уведомление как прочитанное для конкретного пользователя."""
        from models.notification import NotificationRead

        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification:
            return False

        # Проверка прав: можно отметить только своё уведомление или общее (для админов)
        if notification.user_id is not None and notification.user_id != user_id:
            return False

        if user_id is None:
            # Если user_id не передан - старая логика для обратной совместимости
            notification.is_read = True
            self.db.commit()
            return True

        # Проверяем, не отмечал ли уже этот пользователь это уведомление
        existing_read = self.db.query(NotificationRead).filter(
            NotificationRead.notification_id == notification_id,
            NotificationRead.user_id == user_id
        ).first()

        if existing_read:
            return True  # Уже отмечено

        # Создаём запись о прочтении для конкретного пользователя
        new_read = NotificationRead(
            notification_id=notification_id,
            user_id=user_id
        )
        self.db.add(new_read)

        # Если уведомление личное (user_id совпадает), также ставим is_read=True
        if notification.user_id == user_id:
            notification.is_read = True

        self.db.commit()
        return True

    def mark_all_as_read(self, user_id: int = None) -> int:
        """Отметить все уведомления пользователя как прочитанные."""
        from models.notification import NotificationRead

        if user_id is None:
            # Старая логика для обратной совместимости
            count = self.db.query(Notification).filter(
                Notification.is_read == False
            ).update({Notification.is_read: True})
            self.db.commit()
            return count

        # Получаем все непрочитанные уведомления для пользователя
        unread_notifications = self.db.query(Notification).filter(
            Notification.is_read == False,
            (Notification.user_id == user_id) | (Notification.user_id == None)
        ).all()

        count = 0
        for notification in unread_notifications:
            # Проверяем, не отмечал ли уже
            existing_read = self.db.query(NotificationRead).filter(
                NotificationRead.notification_id == notification.id,
                NotificationRead.user_id == user_id
            ).first()

            if not existing_read:
                new_read = NotificationRead(
                    notification_id=notification.id,
                    user_id=user_id
                )
                self.db.add(new_read)

                # Если уведомление личное - ставим is_read=True
                if notification.user_id == user_id:
                    notification.is_read = True

                count += 1

        self.db.commit()
        return count

    def delete_old_notifications(self, days_old: int = 30) -> int:
        """Удалить старые уведомления (старше days_old дней)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        count = self.db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()
        self.db.commit()
        return count

    def notify_return_request(self, return_request: ReturnRequest, user_id: int = None) -> Notification:
        """
        Создание уведомления о запросе на возврат автомобиля.
        """
        try:
            notification = Notification(
                title=f"🔄 Запрос на возврат #{return_request.id}",
                message=(
                    f"Клиент {return_request.client_name} запросил возврат автомобиля "
                    f"{return_request.car_info}.\n"
                    f"Период аренды: {return_request.rental_period}"
                ),
                notification_type="return_request",
                priority="high",
                agreement_id=return_request.rental_id,
                user_id=user_id,  # Привязываем к конкретному пользователю
                is_read=False
            )
            self.db.add(notification)
            self.db.commit()
            logger.info(f"Создано уведомление о запросе на возврат #{return_request.id}")
            return notification
        except Exception as e:
            logger.error(f"Ошибка создания уведомления о возврате: {e}")
            self.db.rollback()
            return None

    def notify_support_request(self, support_request: SupportRequest) -> Notification:
        """
        Создание уведомления об обращении в поддержку.
        """
        try:
            # Проверяем не создавали ли уже уведомление
            existing = self.db.query(Notification).filter(
                Notification.notification_type == "support_request",
                Notification.agreement_id == support_request.id
            ).first()

            if existing:
                return existing

            notification = Notification(
                title=f"📩 Обращение в поддержку #{support_request.id}",
                message=(
                    f"От: {support_request.client_name}\n"
                    f"Тема: {support_request.subject}\n"
                    f"Описание: {support_request.description[:100]}..."
                ),
                notification_type="support_request",
                priority="medium",
                user_id=None,  # None чтобы видели все админы
                agreement_id=support_request.id,  # Сохраняем ID обращения
                is_read=False
            )
            self.db.add(notification)
            self.db.commit()
            logger.info(f"Создано уведомление об обращении в поддержку #{support_request.id}")
            return notification
        except Exception as e:
            logger.error(f"Ошибка создания уведомления об обращении: {e}")
            self.db.rollback()
            return None

    def get_return_request_notifications(self, user_id: int = None, limit: int = 20) -> list:
        """Получение уведомлений о запросах на возврат."""
        query = self.db.query(Notification).filter(
            Notification.notification_type == "return_request"
        )

        if user_id is not None:
            query = query.filter(
                (Notification.user_id == user_id) | (Notification.user_id == None)
            )

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_support_request_notifications(self, user_id: int = None, limit: int = 20) -> list:
        """Получение уведомлений об обращениях в поддержку."""
        query = self.db.query(Notification).filter(
            Notification.notification_type == "support_request"
        )

        if user_id is not None:
            query = query.filter(
                (Notification.user_id == user_id) | (Notification.user_id == None)
            )

        return query.order_by(Notification.created_at.desc()).limit(limit).all()