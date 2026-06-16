"""
Утилиты для работы с таблицами.
"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem


def setup_table_row_height(table: QTableWidget, min_height: int = 40):
    """
    Устанавливает минимальную высоту для всех строк таблицы.

    Args:
        table: Таблица QTableWidget
        min_height: Минимальная высота строки в пикселях (по умолчанию 40)
    """
    for row in range(table.rowCount()):
        table.setRowHeight(row, min_height)


def auto_resize_table_rows(table: QTableWidget, min_height: int = 40):
    """
    Автоматически подстраивает высоту строк под содержимое,
    но не меньше min_height.

    Args:
        table: Таблица QTableWidget
        min_height: Минимальная высота строки в пикселях (по умолчанию 40)
    """
    table.resizeRowsToContents()

    # Проверяем каждую строку и устанавливаем минимальную высоту
    for row in range(table.rowCount()):
        current_height = table.rowHeight(row)
        if current_height < min_height:
            table.setRowHeight(row, min_height)