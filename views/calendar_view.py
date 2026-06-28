from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QDateEdit, QScrollArea, QFrame, QToolTip, QMessageBox,
                             QDialog, QTextEdit)
from PyQt6.QtCore import Qt, QDate, QRectF, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QCursor
from database import SessionLocal
from controllers.calendar_controller import CalendarController
from datetime import date, timedelta


class DetailDialog(QDialog):
    """Диалог просмотра деталей записи."""

    def __init__(self, title: str, details: dict, record_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel(title)
        header.setObjectName("section_header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMinimumHeight(250)

        if record_type == "agreement":
            html = f"""
            <h3>📝 Договор аренды №{details.get('id', 'N/A')}</h3>
            <table style="width: 100%; font-size: 14px;">
                <tr><td><b>Клиент:</b></td><td>{details.get('client', 'N/A')}</td></tr>
                <tr><td><b>Автомобиль:</b></td><td>{details.get('car', 'N/A')}</td></tr>
                <tr><td><b>Начало:</b></td><td>{details.get('start_date', 'N/A')}</td></tr>
                <tr><td><b>Окончание:</b></td><td>{details.get('end_date', 'N/A')}</td></tr>
                <tr><td><b>Длительность:</b></td><td>{details.get('days', 0)} дн.</td></tr>
                <tr><td><b>Стоимость:</b></td><td><b>{details.get('total_cost', 0)} руб.</b></td></tr>
                <tr><td><b>Статус:</b></td><td>{details.get('status', 'N/A')}</td></tr>
            </table>
            """
        elif record_type == "maintenance":
            html = f"""
            <h3>🔧 Техническое обслуживание №{details.get('id', 'N/A')}</h3>
            <table style="width: 100%; font-size: 14px;">
                <tr><td><b>Автомобиль:</b></td><td>{details.get('car', 'N/A')}</td></tr>
                <tr><td><b>Тип ТО:</b></td><td>{details.get('type', 'N/A')}</td></tr>
                <tr><td><b>Описание:</b></td><td>{details.get('description', 'N/A')}</td></tr>
                <tr><td><b>Дата ТО:</b></td><td>{details.get('date', 'N/A')}</td></tr>
                <tr><td><b>Следующее ТО:</b></td><td>{details.get('next_date', 'N/A')}</td></tr>
                <tr><td><b>Пробег:</b></td><td>{details.get('mileage', 'N/A')}</td></tr>
                <tr><td><b>Стоимость:</b></td><td>{details.get('cost', 'N/A')}</td></tr>
                <tr><td><b>Выполнил:</b></td><td>{details.get('performed_by', 'N/A')}</td></tr>
                <tr><td><b>Статус:</b></td><td>{details.get('status', 'N/A')}</td></tr>
            </table>
            """
        else:
            html = "<p>Неизвестный тип записи</p>"

        info_text.setHtml(html)
        layout.addWidget(info_text)

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class GanttChartWidget(QWidget):
    """Виджет Gantt-диаграммы бронирований."""
    record_clicked = pyqtSignal(str, int)

    def __init__(self, bookings: list, maintenance_records: list, cars: list,
                 start_date: date, end_date: date, parent=None):
        super().__init__(parent)
        self.bookings = bookings
        self.maintenance_records = maintenance_records
        self.cars = cars
        self.start_date = start_date
        self.end_date = end_date
        self.day_width = 40
        self.row_height = 100  # УВЕЛИЧЕНО с 60 до 100
        self.header_height = 80
        self.car_column_width = 220

        self.all_records = []
        for b in self.bookings:
            self.all_records.append({**b, "record_type": "agreement"})
        for m in self.maintenance_records:
            self.all_records.append({**m, "record_type": "maintenance"})

        self.setMinimumSize(
            self.car_column_width + len(self._get_days()) * self.day_width + 20,
            self.header_height + len(self.cars) * self.row_height + 20
        )
        self.setMouseTracking(True)

    def _get_days(self) -> list:
        days = []
        current = self.start_date
        while current <= self.end_date:
            days.append(current)
            current += timedelta(days=1)
        return days

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        days = self._get_days()
        total_width = self.car_column_width + len(days) * self.day_width

        # Фон
        painter.fillRect(0, 0, self.width(), self.height(), QColor("#F8FAFC"))

        # Заголовок с датами
        painter.fillRect(0, 0, total_width, self.header_height, QColor("#E2E8F0"))
        painter.setPen(QPen(QColor("#475569"), 1))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))

        for i, day in enumerate(days):
            x = self.car_column_width + i * self.day_width
            painter.drawText(
                QRectF(x, 5, self.day_width, 20),
                Qt.AlignmentFlag.AlignCenter,
                day.strftime("%d")
            )
            painter.drawText(
                QRectF(x, 25, self.day_width, 15),
                Qt.AlignmentFlag.AlignCenter,
                day.strftime("%b")
            )

        # Линии сетки
        painter.setPen(QPen(QColor("#CBD5E1"), 0.5))
        for i in range(len(days) + 1):
            x = self.car_column_width + i * self.day_width
            painter.drawLine(x, self.header_height, x, self.header_height + len(self.cars) * self.row_height)

        # Строки автомобилей
        for row, car in enumerate(self.cars):
            y = self.header_height + row * self.row_height

            # Фон строки
            if row % 2 == 0:
                painter.fillRect(self.car_column_width, y, len(days) * self.day_width, self.row_height,
                                 QColor("#FFFFFF"))
            else:
                painter.fillRect(self.car_column_width, y, len(days) * self.day_width, self.row_height,
                                 QColor("#F1F5F9"))

            # Название автомобиля
            painter.setPen(QPen(QColor("#1E293B")))
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))

            # Разбиваем название на строки если длинное
            car_info = car["info"]
            if len(car_info) > 25:
                # Находим разрыв по пробелу
                mid = car_info.rfind(' ', 0, 25)
                if mid > 0:
                    line1 = car_info[:mid]
                    line2 = car_info[mid + 1:]
                else:
                    line1 = car_info[:25]
                    line2 = car_info[25:]

                painter.drawText(
                    QRectF(5, y + 10, self.car_column_width - 10, 20),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    line1
                )
                painter.drawText(
                    QRectF(5, y + 30, self.car_column_width - 10, 20),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    line2
                )
            else:
                painter.drawText(
                    QRectF(5, y + 15, self.car_column_width - 10, 30),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    car_info
                )

            # Полосы договоров (верхняя часть строки)
            for record in self.all_records:
                if record["car_id"] == car["id"] and record["record_type"] == "agreement":
                    self._draw_agreement_bar(painter, record, y, days)

            # Полосы ТО (нижняя часть строки)
            for record in self.all_records:
                if record["car_id"] == car["id"] and record["record_type"] == "maintenance":
                    self._draw_maintenance_bar(painter, record, y, days)

        painter.end()

    def _draw_agreement_bar(self, painter, record, y, days):
        """Отрисовка полосы договора."""
        booking_start = max(record["start_date"], self.start_date)
        booking_end = min(record["end_date"], self.end_date)

        start_day = (booking_start - self.start_date).days
        end_day = (booking_end - self.start_date).days
        duration = end_day - start_day + 1

        x = self.car_column_width + start_day * self.day_width + 2
        bar_width = duration * self.day_width - 4
        bar_height = 35
        bar_y = y + 30  # ← Убедитесь, что это значение

        # Цвет в зависимости от статуса
        if record["status"] == "active":
            color = QColor("#3B82F6")
        elif record["status"] == "completed":
            color = QColor("#10B981")
        else:
            color = QColor("#94A3B8")

        gradient = QLinearGradient(x, bar_y, x, bar_y + bar_height)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color)
        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(110), 1))
        painter.drawRoundedRect(QRectF(x, bar_y, bar_width, bar_height), 4, 4)

        # Текст на полосе
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Segoe UI", 9))

        client_name = record.get('client_name', '')
        if len(client_name) > 30:
            client_name = client_name[:27] + "..."

        text = f"📝 {client_name}"

        if bar_width > 100:
            painter.drawText(
                QRectF(x + 5, bar_y + 5, bar_width - 10, bar_height - 10),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                text
            )

    def _draw_maintenance_bar(self, painter, record, y, days):
        """Отрисовка полосы ТО."""
        m_start = max(record["start_date"], self.start_date)
        m_end = min(record["end_date"], self.end_date)

        start_day = (m_start - self.start_date).days
        end_day = (m_end - self.start_date).days
        duration = end_day - start_day + 1

        x = self.car_column_width + start_day * self.day_width + 2
        bar_width = duration * self.day_width - 4
        bar_height = 35
        bar_y = y + 65  # ← Убедитесь, что это значение

        # Цвет в зависимости от статуса ТО
        if record["status"] == "Выполнено" or record["status"] == "COMPLETED":
            color = QColor("#059669")
        elif record["status"] == "Запланировано" or record["status"] == "SCHEDULED":
            color = QColor("#F59E0B")
        elif record["status"] == "В процессе" or record["status"] == "IN_PROGRESS":
            color = QColor("#8B5CF6")
        else:
            color = QColor("#94A3B8")

        gradient = QLinearGradient(x, bar_y, x, bar_y + bar_height)
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color)
        painter.setBrush(gradient)
        painter.setPen(QPen(color.darker(110), 1))
        painter.drawRoundedRect(QRectF(x, bar_y, bar_width, bar_height), 4, 4)

        # Текст на полосе
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Segoe UI", 9))

        maint_type = record.get('maintenance_type', record.get('description', ''))
        if len(maint_type) > 30:
            maint_type = maint_type[:27] + "..."

        text = f"🔧 {maint_type}"

        if bar_width > 100:
            painter.drawText(
                QRectF(x + 5, bar_y + 5, bar_width - 10, bar_height - 10),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                text
            )

    def mouseMoveEvent(self, event):
        pos = event.position()
        tooltip_text = self._get_record_at(pos.x(), pos.y())
        if tooltip_text:
            QToolTip.showText(QCursor.pos(), tooltip_text, self)
        else:
            QToolTip.hideText()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            record = self._get_record_object_at(pos.x(), pos.y())
            if record:
                self.record_clicked.emit(record["record_type"], record["id"])

    def _get_record_at(self, x, y):
        days = self._get_days()
        for row, car in enumerate(self.cars):
            y_start = self.header_height + row * self.row_height
            if y_start <= y <= y_start + self.row_height:
                for record in self.all_records:
                    if record["car_id"] == car["id"]:
                        rect = self._get_record_rect(record, y_start, days)
                        if rect and rect.contains(x, y):
                            if record["record_type"] == "agreement":
                                return f"📝 Договор №{record['id']}\n{record.get('client_name', '')}\n{record['start_date'].strftime('%d.%m.%Y')} - {record['end_date'].strftime('%d.%m.%Y')}\n{record['status']}"
                            else:
                                return f"🔧 ТО №{record['id']}\n{record.get('maintenance_type', '')}\n{record['start_date'].strftime('%d.%m.%Y')}\n{record['status']}"
        return None

    def _get_record_object_at(self, x, y):
        days = self._get_days()
        for row, car in enumerate(self.cars):
            y_start = self.header_height + row * self.row_height
            if y_start <= y <= y_start + self.row_height:
                for record in self.all_records:
                    if record["car_id"] == car["id"]:
                        rect = self._get_record_rect(record, y_start, days)
                        if rect and rect.contains(x, y):
                            return record
        return None

    def _get_record_rect(self, record, y_start, days):
        if record["record_type"] == "agreement":
            booking_start = max(record["start_date"], self.start_date)
            booking_end = min(record["end_date"], self.end_date)
            start_day = (booking_start - self.start_date).days
            end_day = (booking_end - self.start_date).days
            duration = end_day - start_day + 1
            x = self.car_column_width + start_day * self.day_width + 2
            bar_width = duration * self.day_width - 4
            bar_height = 35
            bar_y = y_start + 30
            return QRectF(x, bar_y, bar_width, bar_height)
        else:
            m_start = max(record["start_date"], self.start_date)
            m_end = min(record["end_date"], self.end_date)
            start_day = (m_start - self.start_date).days
            end_day = (m_end - self.start_date).days
            duration = end_day - start_day + 1
            x = self.car_column_width + start_day * self.day_width + 2
            bar_width = duration * self.day_width - 4
            bar_height = 35
            bar_y = y_start + 65
            return QRectF(x, bar_y, bar_width, bar_height)


class CalendarWidget(QWidget):
    """Виджет раздела «Календарь бронирований»."""

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user  # Получаем текущего пользователя
        self.db = SessionLocal()
        self.controller = CalendarController(self.db)


        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Проверка прав (календарь доступен всем авторизованным пользователям)
        # Если нужно ограничить - добавьте проверку has_permission('view_calendar')

        header_label = QLabel("📅 Календарь бронирований")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        date_panel = QHBoxLayout()
        date_panel.addWidget(QLabel("Период с:"))

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setMinimumHeight(40)
        date_panel.addWidget(self.start_date_edit)

        date_panel.addWidget(QLabel("по:"))

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(30))
        self.end_date_edit.setMinimumHeight(40)
        date_panel.addWidget(self.end_date_edit)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.clicked.connect(self.load_data)
        date_panel.addWidget(self.refresh_btn)

        date_panel.addStretch()
        layout.addLayout(date_panel)

        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Легенда:"))

        legend_active = QFrame()
        legend_active.setStyleSheet("background-color: #3B82F6; border-radius: 5px;")
        legend_active.setFixedSize(20, 20)
        legend_layout.addWidget(legend_active)
        legend_layout.addWidget(QLabel("Активный договор"))

        legend_completed = QFrame()
        legend_completed.setStyleSheet("background-color: #10B981; border-radius: 5px;")
        legend_completed.setFixedSize(20, 20)
        legend_layout.addWidget(legend_completed)
        legend_layout.addWidget(QLabel("Завершён"))

        legend_cancelled = QFrame()
        legend_cancelled.setStyleSheet("background-color: #94A3B8; border-radius: 5px;")
        legend_cancelled.setFixedSize(20, 20)
        legend_layout.addWidget(legend_cancelled)
        legend_layout.addWidget(QLabel("Отменён"))

        legend_layout.addSpacing(20)

        legend_maint_scheduled = QFrame()
        legend_maint_scheduled.setStyleSheet("background-color: #F59E0B; border-radius: 5px;")
        legend_maint_scheduled.setFixedSize(20, 20)
        legend_layout.addWidget(legend_maint_scheduled)
        legend_layout.addWidget(QLabel("ТО запланировано"))

        legend_maint_completed = QFrame()
        legend_maint_completed.setStyleSheet("background-color: #059669; border-radius: 5px;")
        legend_maint_completed.setFixedSize(20, 20)
        legend_layout.addWidget(legend_maint_completed)
        legend_layout.addWidget(QLabel("ТО выполнено"))

        legend_maint_progress = QFrame()
        legend_maint_progress.setStyleSheet("background-color: #8B5CF6; border-radius: 5px;")
        legend_maint_progress.setFixedSize(20, 20)
        legend_layout.addWidget(legend_maint_progress)
        legend_layout.addWidget(QLabel("ТО в процессе"))

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        hint_label = QLabel("💡 Наведите на запись для подробностей. Кликните для открытия деталей.")
        hint_label.setObjectName("hint_label")
        layout.addWidget(hint_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(400)
        layout.addWidget(self.scroll_area)

        self.load_data()

    def load_data(self):
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()

        bookings = self.controller.get_bookings_for_period(start_date, end_date)
        maintenance_records = self.controller.get_maintenance_for_period(start_date, end_date)
        cars = self.controller.get_all_cars()

        gantt_widget = GanttChartWidget(bookings, maintenance_records, cars, start_date, end_date)
        gantt_widget.record_clicked.connect(self.on_record_clicked)
        self.scroll_area.setWidget(gantt_widget)

    def on_record_clicked(self, record_type: str, record_id: int):
        if record_type == "agreement":
            details = self.controller.get_agreement_details(record_id)
            if details:
                dialog = DetailDialog("Договор аренды", details, "agreement", self)
                dialog.exec()
        elif record_type == "maintenance":
            details = self.controller.get_maintenance_details(record_id)
            if details:
                dialog = DetailDialog("Техническое обслуживание", details, "maintenance", self)
                dialog.exec()

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)