import sys
import os

# Добавляем корневую папку проекта в sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Импортируем модели из десктопной СУ
from models.car import Car
from models.client import Client
from models.agreement import RentalAgreement, AgreementStatus
from models.penalty import Penalty, PenaltyType, PenaltyStatus
from models.user import User, UserRole
from return_request import ReturnRequest, ReturnRequestStatus
from support_request import SupportRequest, SupportRequestStatus

# Экспортируем все модели
__all__ = [
    'Car', 'Client', 'RentalAgreement', 'AgreementStatus',
    'Penalty', 'PenaltyType', 'PenaltyStatus',
    'User', 'UserRole',
    'ReturnRequest', 'ReturnRequestStatus',
    'SupportRequest', 'SupportRequestStatus'
]