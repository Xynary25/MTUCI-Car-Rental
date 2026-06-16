from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QScrollArea, QWidget, QFrame, QGridLayout, QSizePolicy)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os


class CarDetailDialog(QDialog):
    """Диалог подробного просмотра автомобиля с фотографией."""

    def __init__(self, car_data: dict, parent=None):
        super().__init__(parent)
        self.car_data = car_data
        self.setWindowTitle(f"{car_data['brand']} {car_data['model']} - Подробная информация")
        self.resize(600, 400)
        self.setMinimumSize(300, 200)
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Заголовок — через objectName
        title = QLabel(f"{self.car_data['brand']} {self.car_data['model']}")
        title.setObjectName("detail_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Фотография автомобиля
        self.image_label = QLabel()
        self.image_label.setObjectName("detail_image")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(600, 350)  # Минимальный размер фото
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #F1F5F9;
                border-radius: 10px;
                border: 2px solid #E2E8F0;
            }
        """)

        # Загрузка изображения
        image_path = self.car_data.get('image_path')
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.set_placeholder_image()
        else:
            self.set_placeholder_image()

        layout.addWidget(self.image_label)

        # Характеристики в виде сетки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(15)

        specs = [
            ("🚗 Гос. номер:", self.car_data.get('license_plate', 'N/A')),
            ("📅 Год выпуска:", str(self.car_data.get('year', 'N/A'))),
            ("️ Трансмиссия:", self.car_data.get('transmission', 'N/A')),
            (" Тип топлива:", self.car_data.get('fuel_type', 'N/A')),
            ("🔧 Объем двигателя:", self.car_data.get('engine_volume', 'N/A')),
            ("💪 Мощность:",
             f"{self.car_data.get('engine_power', 'N/A')} л.с." if self.car_data.get('engine_power') else "N/A"),
            ("🎨 Цвет:", self.car_data.get('color', 'N/A')),
            ("🚙 Тип кузова:", self.car_data.get('body_type', 'N/A')),
            ("👥 Мест:", str(self.car_data.get('seats', 'N/A')) if self.car_data.get('seats') else "N/A"),
            ("💰 Стоимость аренды:", f"{self.car_data.get('daily_rate', 0)} руб./сутки"),
            ("✅ Статус:", "Доступен" if self.car_data.get('is_available') else "Забронирован/В аренде"),
        ]

        for i, (label, value) in enumerate(specs):
            lbl_name = QLabel(label)
            lbl_name.setObjectName("spec_label")
            lbl_value = QLabel(value)
            lbl_value.setObjectName("spec_value")
            lbl_value.setMinimumWidth(250)

            grid_layout.addWidget(lbl_name, i // 2, (i % 2) * 2)
            grid_layout.addWidget(lbl_value, i // 2, (i % 2) * 2 + 1)

        # Описание
        if self.car_data.get('description'):
            desc_label = QLabel("📝 Описание:")
            desc_label.setObjectName("detail_desc_title")
            grid_layout.addWidget(desc_label, len(specs) // 2 + 1, 0, 1, 4)

            desc_text = QLabel(self.car_data['description'])
            desc_text.setObjectName("detail_desc_text")
            desc_text.setWordWrap(True)
            grid_layout.addWidget(desc_text, len(specs) // 2 + 2, 0, 1, 4)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def set_placeholder_image(self):
        """Установка заглушки, если фото нет."""
        self.image_label.setObjectName("detail_image_placeholder")
        self.image_label.setText("📷 Фотография отсутствует")
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #E2E8F0;
                border-radius: 10px;
                border: 2px dashed #94A3B8;
                color: #64748B;
                font-size: 18px;
                padding: 20px;
            }
        """)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


class CarDetailDialog(QDialog):
    """Диалог подробного просмотра автомобиля с фотографией."""

    def __init__(self, car_data: dict, parent=None):
        super().__init__(parent)
        self.car_data = car_data
        self.setWindowTitle(f"{car_data['brand']} {car_data['model']} - Подробная информация")
        self.resize(800, 700)
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel(f"{self.car_data['brand']} {self.car_data['model']}")
        title.setObjectName("detail_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Фотография автомобиля
        self.image_label = QLabel()
        self.image_label.setObjectName("detail_image")
        self.image_label.setMinimumSize(600, 350)
        self.image_label.setMaximumSize(800, 500)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Загрузка изображения
        image_path = self.car_data.get('image_path')
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.set_placeholder_image()
        else:
            self.set_placeholder_image()

        layout.addWidget(self.image_label)

        # Характеристики в виде сетки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(15)

        specs = [
            ("🚗 Гос. номер:", self.car_data.get('license_plate', 'N/A')),
            ("📅 Год выпуска:", str(self.car_data.get('year', 'N/A'))),
            ("⚙️ Трансмиссия:", self.car_data.get('transmission', 'N/A')),
            ("⛽ Тип топлива:", self.car_data.get('fuel_type', 'N/A')),
            ("🔧 Объем двигателя:", self.car_data.get('engine_volume', 'N/A')),
            (" Мощность:",
             f"{self.car_data.get('engine_power', 'N/A')} л.с." if self.car_data.get('engine_power') else "N/A"),
            ("🎨 Цвет:", self.car_data.get('color', 'N/A')),
            (" Тип кузова:", self.car_data.get('body_type', 'N/A')),
            ("👥 Мест:", str(self.car_data.get('seats', 'N/A')) if self.car_data.get('seats') else "N/A"),
            ("💰 Стоимость аренды:", f"{self.car_data.get('daily_rate', 0)} руб./сутки"),
            ("✅ Статус:", "Доступен" if self.car_data.get('is_available') else "Забронирован/В аренде"),
        ]

        for i, (label, value) in enumerate(specs):
            lbl_name = QLabel(label)
            lbl_name.setObjectName("spec_label")
            lbl_value = QLabel(value)
            lbl_value.setObjectName("spec_value")
            lbl_value.setMinimumWidth(250)

            grid_layout.addWidget(lbl_name, i // 2, (i % 2) * 2)
            grid_layout.addWidget(lbl_value, i // 2, (i % 2) * 2 + 1)

        # Описание
        if self.car_data.get('description'):
            desc_label = QLabel("📝 Описание:")
            desc_label.setObjectName("detail_desc_title")
            grid_layout.addWidget(desc_label, len(specs) // 2 + 1, 0, 1, 4)

            desc_text = QLabel(self.car_data['description'])
            desc_text.setObjectName("detail_desc_text")
            desc_text.setWordWrap(True)
            grid_layout.addWidget(desc_text, len(specs) // 2 + 2, 0, 1, 4)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def set_placeholder_image(self):
        """Установка заглушки, если фото нет."""
        self.image_label.setText("📷 Фотография отсутствует")
        self.image_label.setObjectName("detail_image_placeholder")