from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum
import hashlib
import secrets
import json


class UserRole(enum.Enum):
    SUPER_ADMIN = "superadmin"  # Главный Администратор (неизменяемый)
    ADMIN = "admin"  # Полный доступ
    MANAGER = "manager"  # Управление договорами, клиентами, авто
    OPERATOR = "operator"  # Только просмотр и создание договоров


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.OPERATOR, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    salt = Column(String(32), nullable=False)

    # Хранение индивидуальных прав в JSON
    custom_permissions = Column(Text, nullable=True)

    def set_password(self, password: str):
        self.salt = secrets.token_hex(16)
        self.password_hash = self._hash_password(password, self.salt)

    def check_password(self, password: str) -> bool:
        return self.password_hash == self._hash_password(password, self.salt)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def get_custom_permissions(self) -> list:
        if self.custom_permissions:
            try:
                return json.loads(self.custom_permissions)
            except:
                return []
        return []

    def set_custom_permissions(self, permissions: list):
        self.custom_permissions = json.dumps(permissions)

    def has_permission(self, permission: str) -> bool:
        """Проверка прав с учётом индивидуальных настроек."""
        # SuperAdmin всегда имеет все права
        if self.role == UserRole.SUPER_ADMIN:
            return True

        # Получаем права по роли
        role_permissions = self._get_role_permissions()

        # Получаем индивидуальные права
        custom = self.get_custom_permissions()

        # Если есть индивидуальные права - используем их
        if custom:
            return permission in custom

        # Иначе используем права роли
        return permission in role_permissions

    def _get_role_permissions(self) -> list:
        """Получение прав по роли."""
        permissions_map = {
            UserRole.SUPER_ADMIN: [
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
            ],
            UserRole.ADMIN: [
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
            ],
            UserRole.MANAGER: [
                'view_dashboard', 'view_cars', 'view_clients', 'view_agreements',
                'view_payments', 'view_statistics', 'view_reports',
                'view_notifications', 'view_settings', 'view_about',
                'view_maintenance', 'view_penalties',
                'create_car', 'create_client', 'create_agreement', 'create_payment',
                'create_expense', 'create_maintenance', 'create_penalty',
                'edit_car', 'edit_client', 'edit_agreement',
                'edit_maintenance', 'edit_penalty',
                'export_reports', 'change_password'
            ],
            UserRole.OPERATOR: [
                'view_dashboard', 'view_cars', 'view_clients', 'view_agreements',
                'view_notifications', 'view_about',
                'view_maintenance', 'view_penalties',
                'create_agreement',
                'change_password'
            ]
        }
        return permissions_map.get(self.role, [])

    def to_dict(self) -> dict:
        """Сериализация пользователя в словарь."""
        return {
            "id": self.id,
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%d.%m.%Y %H:%M") if self.created_at else None,
            "last_login": self.last_login.strftime("%d.%m.%Y %H:%M") if self.last_login else None,
            "custom_permissions": self.get_custom_permissions()
        }