"""
Модуль управления правами доступа.
Используется для проверки прав перед выполнением операций.
"""
from enum import Enum


class Permission(Enum):
    """Все возможные права в системе."""
    # Просмотр
    VIEW_CARS = "view_cars"
    VIEW_CLIENTS = "view_clients"
    VIEW_AGREEMENTS = "view_agreements"
    VIEW_PAYMENTS = "view_payments"
    VIEW_STATISTICS = "view_statistics"
    VIEW_AUDIT = "view_audit"
    VIEW_REPORTS = "view_reports"

    # Создание
    CREATE_CAR = "create_car"
    CREATE_CLIENT = "create_client"
    CREATE_AGREEMENT = "create_agreement"
    CREATE_PAYMENT = "create_payment"
    CREATE_EXPENSE = "create_expense"

    # Редактирование
    EDIT_CAR = "edit_car"
    EDIT_CLIENT = "edit_client"
    EDIT_AGREEMENT = "edit_agreement"

    # Удаление
    DELETE_CAR = "delete_car"
    DELETE_CLIENT = "delete_client"
    DELETE_AGREEMENT = "delete_agreement"

    # Административные
    MANAGE_USERS = "manage_users"
    BACKUP_DATABASE = "backup_database"
    EXPORT_REPORTS = "export_reports"
    MANAGE_SETTINGS = "manage_settings"


# Права по ролям
ROLE_PERMISSIONS = {
    "admin": [perm.value for perm in Permission],  # Все права
    "manager": [
        Permission.VIEW_CARS.value,
        Permission.VIEW_CLIENTS.value,
        Permission.VIEW_AGREEMENTS.value,
        Permission.VIEW_PAYMENTS.value,
        Permission.VIEW_STATISTICS.value,
        Permission.VIEW_REPORTS.value,
        Permission.CREATE_CAR.value,
        Permission.CREATE_CLIENT.value,
        Permission.CREATE_AGREEMENT.value,
        Permission.CREATE_PAYMENT.value,
        Permission.CREATE_EXPENSE.value,
        Permission.EDIT_CAR.value,
        Permission.EDIT_CLIENT.value,
        Permission.EDIT_AGREEMENT.value,
        Permission.EXPORT_REPORTS.value,
    ],
    "operator": [
        Permission.VIEW_CARS.value,
        Permission.VIEW_CLIENTS.value,
        Permission.VIEW_AGREEMENTS.value,
        Permission.CREATE_AGREEMENT.value,
        Permission.VIEW_REPORTS.value,
    ]
}


def check_permission(user_role: str, permission: Permission) -> bool:
    """Проверка наличия права у роли."""
    return permission.value in ROLE_PERMISSIONS.get(user_role, [])