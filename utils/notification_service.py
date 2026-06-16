from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from models.notification import Notification
from models.agreement import RentalAgreement, AgreementStatus
from models.car import Car
from models.client import Client
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис управления уведомлениями о возвратах автомобилей."""

    def __init__(self, db_session: Session):
        self.db = db_session

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
                Notification.user_id == user_id,  # ИСПРАВЛЕНИЕ: проверка по user_id
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
                    user_id=user_id  # ИСПРАВЛЕНИЕ: привязка к пользователю
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
                Notification.user_id == user_id,  # ИСПРАВЛЕНИЕ: проверка по user_id
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
                    user_id=user_id  # ИСПРАВЛЕНИЕ: привязка к пользователю
                )
                self.db.add(notification)
                notifications.append(notification)
                logger.warning(f"Создано уведомление о просрочке: {title}")

        self.db.commit()
        return notifications

    def get_unread_notifications(self, user_id: int = None, limit: int = 50) -> list:
        """Получение непрочитанных уведомлений для конкретного пользователя."""
        query = self.db.query(Notification).filter(
            Notification.is_read == False
        )

        # Если передан user_id, фильтруем только его уведомления
        # Если None - показываем все (для обратной совместимости)
        if user_id is not None:
            query = query.filter(
                (Notification.user_id == user_id) | (Notification.user_id == None)
            )

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_all_notifications(self, user_id: int = None, limit: int = 100) -> list:
        """Получение всех уведомлений для конкретного пользователя."""
        query = self.db.query(Notification)

        # Если передан user_id, фильтруем только его уведомления
        if user_id is not None:
            query = query.filter(
                (Notification.user_id == user_id) | (Notification.user_id == None)
            )

        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def mark_as_read(self, notification_id: int, user_id: int = None) -> bool:
        """Отметить уведомление как прочитанное."""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if notification:
            # Можно отметить как прочитанное только свое уведомление
            if user_id is None or notification.user_id == user_id or notification.user_id is None:
                notification.is_read = True
                self.db.commit()
                return True
        return False

    def mark_all_as_read(self, user_id: int = None) -> int:
        """Отметить все уведомления пользователя как прочитанные."""
        query = self.db.query(Notification).filter(
            Notification.is_read == False
        )

        if user_id is not None:
            query = query.filter(
                (Notification.user_id == user_id) | (Notification.user_id == None)
            )

        count = query.update({Notification.is_read: True})
        self.db.commit()
        return count

    def get_unread_count(self, user_id: int = None) -> int:
        """Получить количество непрочитанных уведомлений пользователя."""
        query = self.db.query(Notification).filter(
            Notification.is_read == False
        )

        if user_id is not None:
            query = query.filter(
                (Notification.user_id == user_id) | (Notification.user_id == None)
            )

        return query.count()

    def delete_old_notifications(self, days_old: int = 30) -> int:
        """Удалить старые уведомления (старше days_old дней)."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        count = self.db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()
        self.db.commit()
        return count