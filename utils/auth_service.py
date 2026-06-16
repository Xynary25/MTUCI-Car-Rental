from sqlalchemy.orm import Session
from models.user import User, UserRole
from models.audit_log import AuditLog, ActionType
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Сервис аутентификации и авторизации."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя."""
        user = self.db.query(User).filter(
            User.username == username,
            User.is_active == True
        ).first()

        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            self.db.commit()
            self._log_action(user, "AUTH", "User", "Успешный вход в систему")
            logger.info(f"Пользователь {username} вошёл в систему")
            return user

        if user:
            self._log_action(user, "AUTH", "User", "Неудачная попытка входа (неверный пароль)")
        else:
            logger.warning(f"Попытка входа с несуществующим пользователем: {username}")

        return None

    def create_user(self, username: str, password: str, full_name: str,
                    email: str, role: UserRole, created_by: User,
                    custom_permissions: list = None) -> Dict[str, Any]:
        """Создание нового пользователя."""
        # Проверка: только SuperAdmin может создавать SuperAdmin
        if username == "superadmin" or role.value == "superadmin":
            if created_by.username != "superadmin":
                return {"success": False,
                        "error": "Только Главный Администратор может создавать Главных Администраторов"}

        if not created_by.has_permission('create_user') and created_by.username != "superadmin":
            return {"success": False, "error": "Недостаточно прав для создания пользователей"}

        existing = self.db.query(User).filter(User.username == username).first()
        if existing:
            return {"success": False, "error": "Пользователь с таким логином уже существует"}

        if email:
            existing_email = self.db.query(User).filter(User.email == email).first()
            if existing_email:
                return {"success": False, "error": "Пользователь с таким email уже существует"}

        if len(password) < 6:
            return {"success": False, "error": "Пароль должен содержать минимум 6 символов"}

        new_user = User(
            username=username,
            full_name=full_name,
            email=email,
            role=role
        )
        new_user.set_password(password)

        # Устанавливаем индивидуальные права если указаны
        if custom_permissions:
            new_user.set_custom_permissions(custom_permissions)

        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            self._log_action(
                created_by, "CREATE", "User",
                f"Создан пользователь {username} с ролью {role.value}"
            )
            logger.info(f"Создан пользователь {username}")
            return {"success": True, "data": new_user}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка при создании: {str(e)}"}

    def update_user(self, user_id: int, data: dict, admin: User) -> Dict[str, Any]:
        """Обновление данных пользователя администратором."""
        import logging
        logger = logging.getLogger(__name__)

        logger.info("=" * 60)
        logger.info("ВХОД В update_user()")
        logger.info(f"ID пользователя для обновления: {user_id}")
        logger.info(f"Администратор: {admin.username} (роль: {admin.role.value})")
        logger.info(f"Полученные данные: {list(data.keys())}")
        logger.info(f"Содержимое data: {data}")
        logger.info("=" * 60)

        if not admin.has_permission('edit_user'):
            logger.error(f"Недостаточно прав у {admin.username}")
            return {"success": False, "error": "Недостаточно прав"}

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"Пользователь с ID {user_id} не найден")
            return {"success": False, "error": "Пользователь не найден"}

        logger.info(f"Найден пользователь: {user.username} (ID: {user.id})")
        logger.info(f"Текущая соль: {user.salt}")
        logger.info(f"Текущий хеш пароля: {user.password_hash[:20]}...")

        if 'username' in data and data['username'] != user.username:
            existing = self.db.query(User).filter(User.username == data['username']).first()
            if existing:
                logger.error(f"Логин '{data['username']}' уже занят")
                return {"success": False, "error": "Логин уже занят"}
            logger.info(f"Смена логина: {user.username} -> {data['username']}")
            user.username = data['username']

        if 'full_name' in data:
            logger.info(f"Обновление ФИО: {user.full_name} -> {data['full_name']}")
            user.full_name = data['full_name']

        if 'email' in data:
            logger.info(f"Обновление email: {user.email} -> {data['email']}")
            user.email = data['email']

        if 'role' in data:
            try:
                old_role = user.role
                user.role = UserRole(data['role'])
                logger.info(f"Смена роли: {old_role.value} -> {user.role.value}")
            except ValueError:
                logger.error(f"Недопустимая роль: {data['role']}")
                return {"success": False, "error": "Недопустимая роль"}

        if 'is_active' in data:
            if user.id == admin.id and data['is_active'] == False:
                logger.error("Попытка деактивировать самого себя")
                return {"success": False, "error": "Нельзя деактивировать самого себя"}
            logger.info(f"Смена статуса активности: {user.is_active} -> {data['is_active']}")
            user.is_active = data['is_active']

        # === КРИТИЧЕСКОЕ ЛОГИРОВАНИЕ ПАРОЛЯ ===
        if 'password' in data and data['password']:
            logger.info("=" * 60)
            logger.info("ОБНАРУЖЕНО ОБНОВЛЕНИЕ ПАРОЛЯ!")
            logger.info(f"Открытый пароль из data: '{data['password']}'")
            logger.info(f"Длина пароля: {len(data['password'])}")

            if len(data['password']) < 6:
                logger.error("Пароль слишком короткий")
                return {"success": False, "error": "Пароль должен содержать минимум 6 символов"}

            logger.info("Вызываем user.set_password()...")
            user.set_password(data['password'])

            logger.info(f"НОВАЯ соль: {user.salt}")
            logger.info(f"НОВЫЙ хеш пароля: {user.password_hash[:20]}...")
            logger.info("=" * 60)
        else:
            logger.info("Пароль НЕ обновляется")
        # === КОНЕЦ ЛОГИРОВАНИЯ ПАРОЛЯ ===

        if 'custom_permissions' in data:
            logger.info(f"Обновление индивидуальных прав: {data['custom_permissions']}")
            user.set_custom_permissions(data['custom_permissions'])

        try:
            logger.info("Выполняем db.commit()...")
            self.db.commit()
            logger.info("commit() выполнен успешно!")

            # === ПРОВЕРКА ПОСЛЕ COMMIT ===
            logger.info("=" * 60)
            logger.info("ПРОВЕРКА ПОСЛЕ COMMIT:")
            self.db.refresh(user)
            logger.info(f"После refresh - соль: {user.salt}")
            logger.info(f"После refresh - хеш: {user.password_hash[:20]}...")

            # Проверяем что пароль работает
            if 'password' in data and data['password']:
                check_result = user.check_password(data['password'])
                logger.info(f"Проверка пароля сразу после сохранения: {check_result}")
            logger.info("=" * 60)
            # === КОНЕЦ ПРОВЕРКИ ===

            self._log_action(
                admin, "UPDATE", "User",
                f"Обновлён пользователь {user.username}"
            )
            logger.info(f"Пользователь {user.username} успешно обновлён")
            return {"success": True}
        except Exception as e:
            logger.error(f"Ошибка при сохранении: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def change_password(self, user: User, old_password: str, new_password: str) -> Dict[str, Any]:
        """Смена пароля пользователем."""
        if not user.check_password(old_password):
            return {"success": False, "error": "Неверный текущий пароль"}

        if len(new_password) < 6:
            return {"success": False, "error": "Пароль должен содержать минимум 6 символов"}

        user.set_password(new_password)
        self.db.commit()
        self._log_action(user, "UPDATE", "User", "Смена пароля")
        return {"success": True}

    def get_all_users(self) -> List[User]:
        """Получение списка всех пользователей."""
        return self.db.query(User).order_by(User.created_at.desc()).all()

    def delete_user(self, user_id: int, admin: User) -> Dict[str, Any]:
        """Удаление пользователя."""
        if not admin.has_permission('delete_user'):
            return {"success": False, "error": "Недостаточно прав"}

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"success": False, "error": "Пользователь не найден"}

        if user.id == admin.id:
            return {"success": False, "error": "Нельзя удалить самого себя"}

        try:
            self.db.delete(user)
            self.db.commit()
            self._log_action(
                admin, "DELETE", "User",
                f"Удалён пользователь {user.username}"
            )
            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка: {str(e)}"}

    def get_all_permissions(self) -> list:
        """Получение списка всех возможных прав."""
        return [
            'view_dashboard', 'view_cars', 'view_clients', 'view_agreements',
            'view_payments', 'view_statistics', 'view_audit', 'view_reports',
            'view_notifications', 'view_users', 'view_settings', 'view_about',
            'create_car', 'create_client', 'create_agreement', 'create_payment',
            'create_expense', 'create_user',
            'edit_car', 'edit_client', 'edit_agreement', 'edit_user',
            'delete_car', 'delete_client', 'delete_agreement', 'delete_user',
            'export_reports', 'backup_database', 'manage_settings',
            'change_password', 'view_all_users_passwords'
        ]

    def _log_action(self, user: User, action_type: str, entity: str, description: str):
        """Логирование действий."""
        from models.audit_log import AuditLog, ActionType

        # Маппинг строковых типов действий в Enum
        action_type_map = {
            "AUTH": ActionType.AUTH,
            "LOGIN": ActionType.LOGIN,
            "LOGOUT": ActionType.LOGOUT,
            "LOGIN_FAILED": ActionType.LOGIN_FAILED,
            "CREATE": ActionType.CREATE,
            "UPDATE": ActionType.UPDATE,
            "DELETE": ActionType.DELETE,
        }

        enum_action = action_type_map.get(action_type, ActionType.AUTH)

        log = AuditLog(
            action_type=enum_action,
            entity_name=entity,
            entity_id=user.id,
            description=description,
            user_info=f"{user.username} ({user.role.value})"
        )
        self.db.add(log)
        self.db.commit()

    def close(self):
        """Закрытие сессии базы данных."""
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
                print("Сессия AuthService закрыта")
        except Exception as e:
            print(f"Ошибка закрытия сессии AuthService: {e}")


def init_default_users(db_session: Session):
    """Создание тестовых пользователей при первом запуске."""
    users_data = [
        {
            "username": "super",
            "password": "123123",
            "full_name": "Главный Администратор Системы",
            "email": "superadmin@mtuci-rental.ru",
            "role": UserRole.SUPER_ADMIN
        },
        {
            "username": "admin",
            "password": "admin123",
            "full_name": "Администратор системы",
            "email": "admin@mtuci-rental.ru",
            "role": UserRole.ADMIN
        },
        {
            "username": "manager",
            "password": "manager123",
            "full_name": "Менеджер по аренде",
            "email": "manager@mtuci-rental.ru",
            "role": UserRole.MANAGER
        },
        {
            "username": "operator",
            "password": "operator123",
            "full_name": "Оператор пункта проката",
            "email": "operator@mtuci-rental.ru",
            "role": UserRole.OPERATOR
        }
    ]

    for user_data in users_data:
        try:
            # Проверяем существование по username ИЛИ email
            existing_by_username = db_session.query(User).filter(
                User.username == user_data["username"]
            ).first()
            existing_by_email = db_session.query(User).filter(
                User.email == user_data["email"]
            ).first()

            if existing_by_username or existing_by_email:
                # Пользователь уже существует - пропускаем
                logger.info(f"Пользователь {user_data['username']} уже существует, пропускаем")
                continue

            user = User(
                username=user_data["username"],
                full_name=user_data["full_name"],
                email=user_data["email"],
                role=user_data["role"]
            )
            user.set_password(user_data["password"])

            # SuperAdmin получает все права автоматически
            if user_data["role"] == UserRole.SUPER_ADMIN:
                all_perms = [
                    'view_dashboard', 'view_cars', 'view_clients', 'view_agreements',
                    'view_payments', 'view_statistics', 'view_audit', 'view_reports',
                    'view_notifications', 'view_users', 'view_settings', 'view_about',
                    'view_maintenance', 'view_penalties',
                    'create_car', 'create_client', 'create_agreement', 'create_payment',
                    'create_expense', 'create_user', 'create_maintenance', 'create_penalty',
                    'edit_car', 'edit_client', 'edit_agreement', 'edit_user',
                    'edit_maintenance', 'edit_penalty',
                    'delete_car', 'delete_client', 'delete_agreement', 'delete_user',
                    'delete_maintenance', 'delete_penalty',
                    'export_reports', 'backup_database', 'manage_settings',
                    'change_password', 'view_all_users_passwords'
                ]
                user.set_custom_permissions(all_perms)

            db_session.add(user)
            db_session.commit()
            logger.info(f"Создан тестовый пользователь: {user_data['username']}")

        except Exception as e:
            db_session.rollback()
            logger.warning(f"Не удалось создать пользователя {user_data['username']}: {str(e)}")
            continue