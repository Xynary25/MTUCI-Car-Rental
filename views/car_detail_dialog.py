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
        self.resize(1000, 800)
        self.setMinimumSize(600, 400)
        self.setModal(True)

        self.init_ui()
        self.load_car_data(car_data)

    def load_car_data(self, car_data: dict):
        """Загрузка данных автомобиля в форму."""
        from utils.path_utils import url_path_to_absolute

        self.setWindowTitle(f"{car_data.get('brand', '')} {car_data.get('model', '')} - Подробная информация")

        # Загрузка изображения
        image_path = car_data.get('image_path')

        if image_path:
            # Конвертируем URL-путь в абсолютный
            absolute_path = url_path_to_absolute(image_path)
            print(f"🔍 Загрузка фото в CarDetailDialog:")
            print(f"   Исходный путь: {image_path}")
            print(f"   Абсолютный путь: {absolute_path}")
            print(f"   Файл существует: {os.path.exists(absolute_path)}")

            if os.path.exists(absolute_path):
                pixmap = QPixmap(absolute_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    print(f"✅ Фото загружено успешно")
                else:
                    print(f"❌ QPixmap не смог загрузить файл")
                    self.set_placeholder_image()
            else:
                print(f"⚠️ Файл не найден")
                self.set_placeholder_image()
        else:
            print(f"⚠️ image_path не задан")
            self.set_placeholder_image()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title = QLabel(f"{self.car_data['brand']} {self.car_data['model']}")
        title.setObjectName("detail_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #1e293b;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)

        # Фотография автомобиля
        self.image_label = QLabel()
        self.image_label.setObjectName("detail_image")
        self.image_label.setMinimumSize(600, 350)  # Увеличили размер фото
        self.image_label.setMaximumSize(800, 450)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #f1f5f9;
                border-radius: 15px;
                border: 3px solid #e2e8f0;
            }
        """)

        # Загрузка изображения
        from utils.path_utils import url_path_to_absolute

        image_path = self.car_data.get('image_path')
        if image_path:
            # Конвертируем путь
            absolute_path = url_path_to_absolute(image_path)

            if os.path.exists(absolute_path):
                pixmap = QPixmap(absolute_path)
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
        else:
            self.set_placeholder_image()

        layout.addWidget(self.image_label)

        # Характеристики в виде сетки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        content_widget = QWidget()
        grid_layout = QGridLayout(content_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        specs = [
            (" Гос. номер:", self.car_data.get('license_plate', 'N/A')),
            ("📅 Год выпуска:", str(self.car_data.get('year', 'N/A'))),
            ("⚙️ Трансмиссия:", self.car_data.get('transmission', 'N/A')),
            ("⛽ Тип топлива:", self.car_data.get('fuel_type', 'N/A')),
            ("🔧 Объем двигателя:", self.car_data.get('engine_volume', 'N/A')),
            ("💪 Мощность:",
             f"{self.car_data.get('engine_power', 'N/A')} л.с." if self.car_data.get('engine_power') else "N/A"),
            ("🎨 Цвет:", self.car_data.get('color', 'N/A')),
            ("🚙 Тип кузова:", self.car_data.get('body_type', 'N/A')),
            (" Мест:", str(self.car_data.get('seats', 'N/A')) if self.car_data.get('seats') else "N/A"),
            ("💰 Стоимость аренды:", f"{self.car_data.get('daily_rate', 0)} руб./сутки"),
            ("✅ Статус:", "Доступен" if self.car_data.get('is_available') else "Забронирован/В аренде"),
        ]

        for i, (label, value) in enumerate(specs):
            lbl_name = QLabel(label)
            lbl_name.setObjectName("spec_label")
            lbl_name.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #475569;
                    padding: 10px;
                }
            """)

            lbl_value = QLabel(value)
            lbl_value.setObjectName("spec_value")
            lbl_value.setMinimumWidth(300)
            lbl_value.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #1e293b;
                    padding: 10px;
                    background-color: #f8fafc;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                }
            """)

            grid_layout.addWidget(lbl_name, i // 2, (i % 2) * 2)
            grid_layout.addWidget(lbl_value, i // 2, (i % 2) * 2 + 1)

        # Описание
        if self.car_data.get('description'):
            desc_label = QLabel("📝 Описание:")
            desc_label.setObjectName("detail_desc_title")
            desc_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #1e293b;
                    margin-top: 20px;
                }
            """)
            grid_layout.addWidget(desc_label, len(specs) // 2 + 1, 0, 1, 4)

            desc_text = QLabel(self.car_data['description'])
            desc_text.setObjectName("detail_desc_text")
            desc_text.setWordWrap(True)
            desc_text.setStyleSheet("""
                QLabel {
                    font-size: 15px;
                    color: #475569;
                    padding: 15px;
                    background-color: #f8fafc;
                    border-radius: 8px;
                    border: 1px solid #e2e8f0;
                    line-height: 1.6;
                }
            """)
            grid_layout.addWidget(desc_text, len(specs) // 2 + 2, 0, 1, 4)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.setMinimumHeight(50)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
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
