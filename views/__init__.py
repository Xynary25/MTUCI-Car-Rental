from views.main_window import MainWindow
from views.dashboard_view import DashboardWidget
from views.car_view import CarWidget, CarDialog
from views.client_view import ClientWidget, ClientDialog
from views.agreement_view import AgreementWidget, AgreementDialog
from views.statistics_view import StatisticsWidget, ExpenseDialog
from views.report_view import ReportWidget
from views.audit_view import AuditWidget
from views.settings_view import SettingsWidget
from views.about_dialog import AboutDialog
from views.penalty_view import PenaltyWidget, PenaltyDialog
from views.maintenance_view import MaintenanceWidget, MaintenanceDialog
from views.calendar_view import CalendarWidget

__all__ = [
    "MainWindow",
    "DashboardWidget",
    "CarWidget", "CarDialog",
    "ClientWidget", "ClientDialog",
    "AgreementWidget", "AgreementDialog",
    "StatisticsWidget", "ExpenseDialog",
    "ReportWidget",
    "AuditWidget",
    "SettingsWidget",
    "AboutDialog",
    "PenaltyWidget", "PenaltyDialog",
    "MaintenanceWidget", "MaintenanceDialog",
    "CalendarWidget"
]