from PyQt6.QtCore import QObject, pyqtSignal

class GlobalSignals(QObject):
    """Глобальные сигналы приложения."""
    navigate_to_agreement = pyqtSignal(int)  # Сигнал для навигации к договору

# Глобальный экземпляр сигналов
global_signals = GlobalSignals()