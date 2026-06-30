from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QDialog, QFormLayout, QLineEdit, QSpinBox, QCheckBox,
                             QMessageBox, QHeaderView, QAbstractItemView, QLabel, QFileDialog,
                             QComboBox, QGroupBox, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap, QFont
from database import SessionLocal
from controllers.car_controller import CarController
from views.car_detail_dialog import CarDetailDialog
import os
from utils.image_utils import find_car_image, get_available_images


class CarDialog(QDialog):
    """Модальное окно для добавления/редактирования автомобиля."""

    def __init__(self, parent=None, car_data: dict = None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование автомобиля" if car_data else "Добавление автомобиля")
        self.resize(550, 650)
        self.car_data = car_data
        self.image_path = car_data.get('image_path') if car_data else None

        # === ЛОГИРОВАНИЕ ===
        print(f"\n{'=' * 60}")
        print(f"🚗 ОТКРЫТИЕ ДИАЛОГА РЕДАКТИРОВАНИЯ АВТО")
        print(f"{'=' * 60}")
        if car_data:
            print(f"📋 Данные автомобиля:")
            print(f"   ID: {car_data.get('id')}")
            print(f"   Марка: {car_data.get('brand')}")
            print(f"   Модель: {car_data.get('model')}")
            print(f"   Гос. номер: {car_data.get('license_plate')}")
            print(f"   image_path из БД: '{car_data.get('image_path')}'")
            print(f"   self.image_path после присвоения: '{self.image_path}'")
        else:
            print(f"📋 Создание нового автомобиля (car_data = None)")
        print(f"{'=' * 60}\n")

        # Основной layout с прокруткой
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # Создаем scroll area для формы
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        form_widget = QWidget()
        layout = QFormLayout(form_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("Например: Toyota")
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Например: Camry")
        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("Например: А777АА777")

        self.year_input = QSpinBox()
        self.year_input.setRange(2000, 2030)
        self.year_input.setValue(2024)

        self.transmission_combo = QComboBox()
        self.transmission_combo.addItems(["Автомат", "Механика", "Робот", "Вариатор"])

        self.fuel_combo = QComboBox()
        self.fuel_combo.addItems(["Бензин", "Дизель", "Электро", "Гибрид"])

        self.engine_input = QLineEdit()
        self.engine_input.setPlaceholderText("2.5 л")

        self.power_input = QSpinBox()
        self.power_input.setRange(50, 1000)
        self.power_input.setSuffix(" л.с.")
        self.power_input.setValue(150)

        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Например: Белый")

        self.body_combo = QComboBox()
        self.body_combo.addItems(["Седан", "Внедорожник", "Кроссовер", "Хэтчбек", "Универсал", "Минивэн"])

        self.seats_input = QSpinBox()
        self.seats_input.setRange(2, 9)
        self.seats_input.setValue(5)

        self.rate_input = QSpinBox()
        self.rate_input.setRange(1, 100000)
        self.rate_input.setSuffix(" руб./сутки")
        self.rate_input.setValue(3000)

        self.available_check = QCheckBox("Доступен для аренды")
        self.available_check.setChecked(True)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Краткое описание автомобиля")

        # Заполняем данными если редактируем
        if car_data:
            self.brand_input.setText(car_data.get("brand", ""))
            self.model_input.setText(car_data.get("model", ""))
            self.plate_input.setText(car_data.get("license_plate", ""))
            self.year_input.setValue(car_data.get("year", 2024))
            self.engine_input.setText(car_data.get("engine_volume", ""))
            self.color_input.setText(car_data.get("color", ""))
            self.rate_input.setValue(car_data.get("daily_rate", 3000))
            self.desc_input.setText(car_data.get("description", ""))

            self.power_input.setValue(car_data.get("engine_power", 150))
            self.seats_input.setValue(car_data.get("seats", 5))

            transmission = car_data.get("transmission", "Автомат")
            if self.transmission_combo.findText(transmission) != -1:
                self.transmission_combo.setCurrentText(transmission)

            fuel = car_data.get("fuel_type", "Бензин")
            if self.fuel_combo.findText(fuel) != -1:
                self.fuel_combo.setCurrentText(fuel)

            body = car_data.get("body_type", "Седан")
            if self.body_combo.findText(body) != -1:
                self.body_combo.setCurrentText(body)

            is_avail = car_data.get("is_available", True)
            if isinstance(is_avail, str):
                is_avail = is_avail.lower() in ["true", "да", "1", "✓"]
            self.available_check.setChecked(bool(is_avail))

            self.image_path = car_data.get("image_path")

        layout.addRow("<b>Основные данные</b>", QLabel())
        layout.addRow("Марка:", self.brand_input)
        layout.addRow("Модель:", self.model_input)
        layout.addRow("Гос. номер:", self.plate_input)
        layout.addRow("Год выпуска:", self.year_input)

        layout.addRow("<b>Технические характеристики</b>", QLabel())
        layout.addRow("Трансмиссия:", self.transmission_combo)
        layout.addRow("Тип топлива:", self.fuel_combo)
        layout.addRow("Объем двигателя:", self.engine_input)
        layout.addRow("Мощность:", self.power_input)
        layout.addRow("Цвет:", self.color_input)
        layout.addRow("Тип кузова:", self.body_combo)
        layout.addRow("Количество мест:", self.seats_input)

        layout.addRow("<b>Аренда</b>", QLabel())
        layout.addRow("Ставка аренды:", self.rate_input)
        layout.addRow("Описание:", self.desc_input)
        layout.addRow("Статус:", self.available_check)

        # Кнопка выбора фото
        photo_group = QGroupBox("Фотография автомобиля")
        photo_layout = QVBoxLayout(photo_group)

        self.photo_btn = QPushButton("Выбрать фотографию")
        self.photo_btn.setMinimumHeight(45)
        self.photo_btn.clicked.connect(self.select_photo)
        photo_layout.addWidget(self.photo_btn)

        # Создаем photo_preview
        self.photo_preview = QLabel("Фото не выбрано")
        self.photo_preview.setObjectName("photo_preview_label")
        self.photo_preview.setMinimumHeight(150)
        self.photo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_preview.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #F1F5F9;
                border-radius: 8px;
                border: 2px dashed #94A3B8;
                color: #64748B;
            }
        """)
        photo_layout.addWidget(self.photo_preview)

        # === УМНАЯ ЗАГРУЗКА ФОТО ===
        from utils.path_utils import url_path_to_absolute, file_exists, find_image_in_images_dir

        # Если image_path задан из БД, конвертируем его
        if self.image_path and car_data:
            absolute_path = url_path_to_absolute(self.image_path)
            print(f"🔍 Конвертация пути:")
            print(f"   Исходный: {self.image_path}")
            print(f"   Абсолютный: {absolute_path}")
            print(f"   Файл существует: {os.path.exists(absolute_path)}")

            if os.path.exists(absolute_path):
                self.image_path = absolute_path
            else:
                # Файл не найден по пути из БД, ищем в images/
                print(f"⚠️ Файл не найден, ищем в images/")
                auto_photo = find_image_in_images_dir(
                    license_plate=car_data.get("license_plate"),
                    brand=car_data.get("brand"),
                    model=car_data.get("model")
                )
                if auto_photo:
                    self.image_path = auto_photo
                    print(f"✅ Найдено фото в images/: {auto_photo}")
                else:
                    self.image_path = None
                    print(f"❌ Фото не найдено")
        elif car_data:
            # image_path не задан, ищем автоматически
            auto_photo = find_image_in_images_dir(
                license_plate=car_data.get("license_plate"),
                brand=car_data.get("brand"),
                model=car_data.get("model")
            )
            if auto_photo:
                self.image_path = auto_photo
                print(f"✅ Автоматически найдено фото: {auto_photo}")

        if self.image_path and os.path.exists(self.image_path):
            self.update_photo_preview(self.image_path)
            print(f"✅ Превью обновлено")
        else:
            print(f"⚠️ Превью не обновлено (файл не найден)")

        layout.addRow(photo_group)

        # Кнопки сохранения/отмены
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.setMinimumHeight(45)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("❌ Отмена")
        self.cancel_btn.setMinimumHeight(45)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)

        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)

    def select_photo(self):
        """Выбор файла фотографии."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите фотографию", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.image_path = file_path
            self.update_photo_preview(file_path)

    def update_photo_preview(self, path):
        """Обновление превью фотографии."""
        if not hasattr(self, 'photo_preview'):
            return  # Защита если виджет еще не создан

        if not path:
            self.photo_preview.setText("Фото не выбрано")
            self.photo_preview.setStyleSheet("""
                QLabel {
                    padding: 15px;
                    background-color: #F1F5F9;
                    border-radius: 8px;
                    border: 2px dashed #94A3B8;
                    color: #64748B;
                }
            """)
            return

        from utils.path_utils import url_path_to_absolute, file_exists

        absolute_path = url_path_to_absolute(path)

        print(f"🔍 Конвертация пути:")
        print(f"   Исходный: {path}")
        print(f"   Абсолютный: {absolute_path}")
        print(f"   Файл существует: {os.path.exists(absolute_path)}")

        if not os.path.exists(absolute_path):
            self.photo_preview.setText(f"⚠️ Файл не найден:\n{path}")
            self.photo_preview.setStyleSheet("""
                QLabel {
                    padding: 15px;
                    background-color: #FEF3C7;
                    border-radius: 8px;
                    border: 2px dashed #F59E0B;
                    color: #92400E;
                    font-size: 12px;
                }
            """)
            return

        pixmap = QPixmap(absolute_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                200, 150,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.photo_preview.setPixmap(scaled_pixmap)
            self.photo_preview.setText("")
            self.photo_preview.setStyleSheet("""
                QLabel {
                    padding: 5px;
                    background-color: white;
                    border-radius: 8px;
                    border: 2px solid #2563EB;
                }
            """)
            print(f"✅ Фото загружено успешно")
        else:
            self.photo_preview.setText("❌ Ошибка загрузки фото")
            print(f"❌ QPixmap не смог загрузить файл")

    def get_data(self) -> dict:
        return {
            "brand": self.brand_input.text(),
            "model": self.model_input.text(),
            "license_plate": self.plate_input.text(),
            "year": self.year_input.value(),
            "transmission": self.transmission_combo.currentText(),
            "fuel_type": self.fuel_combo.currentText(),
            "engine_volume": self.engine_input.text(),
            "engine_power": self.power_input.value(),
            "color": self.color_input.text(),
            "body_type": self.body_combo.currentText(),
            "seats": self.seats_input.value(),
            "daily_rate": self.rate_input.value(),
            "description": self.desc_input.text(),
            "is_available": self.available_check.isChecked(),
            "image_path": self.image_path
        }


class CarWidget(QWidget):
    """Основной виджет раздела 'Автопарк' с фото и двойным кликом."""

    def __init__(self, current_user=None):
        super().__init__()
        self.db = SessionLocal()
        self.controller = CarController(self.db)
        self.all_cars = []
        self.current_user = current_user  # Получаем пользователя из параметра

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок раздела
        header_label = QLabel("🚗 Управление автопарком")
        header_label.setObjectName("section_header")
        layout.addWidget(header_label)

        # Панель поиска
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по марке, модели или гос. номеру...")
        self.search_input.textChanged.connect(self.filter_cars)
        self.search_input.setMaximumWidth(400)
        self.search_input.setMinimumHeight(40)
        self.search_input.setObjectName("search_input")

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addStretch()

        layout.addLayout(search_layout)

        # Панель инструментов — кнопки создаются ВСЕГДА, проверка прав при клике
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить автомобиль")
        self.add_btn.setMinimumHeight(45)
        self.add_btn.clicked.connect(self.add_car)

        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setMinimumHeight(45)
        self.edit_btn.clicked.connect(self.edit_car)

        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setMinimumHeight(45)
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.delete_car)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setMinimumHeight(45)
        self.refresh_btn.clicked.connect(self.load_data)

        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        toolbar.addStretch()
        toolbar.addWidget(self.refresh_btn)

        layout.addLayout(toolbar)

        # Подсказка о двойном клике
        hint_label = QLabel("💡 Двойной клик по автомобилю для просмотра подробной информации с фотографией")
        hint_label.setObjectName("hint_label")
        layout.addWidget(hint_label)

        # Таблица данных
        self.table = QTableWidget()
        self.table.setObjectName("car_table")
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "ID", "Марка", "Модель", "Год", "Гос. номер", "КПП",
            "Топливо", "Двигатель", "Мощность", "Доступен", "Ставка (руб.)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.show_car_details)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        """Загрузка данных из контроллера в таблицу."""
        self.all_cars = self.controller.get_all_cars()
        self.display_cars(self.all_cars)

    def display_cars(self, cars):
        """Отображение автомобилей в таблице."""
        self.table.setRowCount(len(cars))
        for row, car in enumerate(cars):
            self.table.setItem(row, 0, QTableWidgetItem(str(car["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(car["brand"]))
            self.table.setItem(row, 2, QTableWidgetItem(car["model"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(car.get("year", "N/A"))))
            self.table.setItem(row, 4, QTableWidgetItem(car["license_plate"]))
            self.table.setItem(row, 5, QTableWidgetItem(car.get("transmission", "N/A")))
            self.table.setItem(row, 6, QTableWidgetItem(car.get("fuel_type", "N/A")))
            self.table.setItem(row, 7, QTableWidgetItem(car.get("engine_volume", "N/A")))
            self.table.setItem(row, 8, QTableWidgetItem(
                f"{car.get('engine_power', 'N/A')} л.с." if car.get('engine_power') else "N/A"
            ))

            is_available = car.get("is_available", False)
            if is_available:
                availability_item = QTableWidgetItem("✓ Доступен")
                availability_item.setForeground(Qt.GlobalColor.darkGreen)
            else:
                availability_item = QTableWidgetItem("✗ Занят")
                availability_item.setForeground(Qt.GlobalColor.red)

            self.table.setItem(row, 9, availability_item)
            self.table.setItem(row, 10, QTableWidgetItem(str(car["daily_rate"])))
        from utils.table_utils import auto_resize_table_rows
        auto_resize_table_rows(self.table, min_height=40)

    def filter_cars(self, search_text):
        """Фильтрация автомобилей по поисковому запросу."""
        search_text = search_text.lower().strip()
        if not search_text:
            self.display_cars(self.all_cars)
            return

        filtered = [
            car for car in self.all_cars
            if (search_text in car["brand"].lower() or
                search_text in car["model"].lower() or
                search_text in car["license_plate"].lower())
        ]
        self.display_cars(filtered)

    def show_car_details(self, index):
        """Показ подробной информации об автомобиле по двойному клику."""
        row = index.row()
        car_id = int(self.table.item(row, 0).text())
        car_data = next((c for c in self.all_cars if c["id"] == car_id), None)

        if car_data:
            dialog = CarDetailDialog(car_data, self)
            dialog.exec()

    def add_car(self):
        # Проверка прав перед действием
        if self.current_user and not self.current_user.has_permission('create_car'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для добавления автомобилей")
            return

        dialog = CarDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            result = self.controller.add_car(data)
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "Автомобиль успешно добавлен!")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def edit_car(self):
        # Проверка прав перед действием
        if self.current_user and not self.current_user.has_permission('edit_car'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для редактирования автомобилей")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите автомобиль для редактирования")
            return

        row = selected[0].row()
        car_id = int(self.table.item(row, 0).text())
        car_data = next((c for c in self.all_cars if c["id"] == car_id), None)

        if not car_data:
            return

        dialog = CarDialog(self, car_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            result = self.controller.update_car(car_id, data)
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "Данные автомобиля обновлены!")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def delete_car(self):
        # Проверка прав перед действием
        if self.current_user and not self.current_user.has_permission('delete_car'):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав для удаления автомобилей")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите автомобиль для удаления")
            return

        row = selected[0].row()
        car_id = int(self.table.item(row, 0).text())
        license_plate = self.table.item(row, 4).text()

        reply = QMessageBox.question(self, "Подтверждение", f"Удалить автомобиль {license_plate}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            result = self.controller.delete_car(car_id)
            if result["success"]:
                self.load_data()
                QMessageBox.information(self, "Успех", "Автомобиль удален!")
            else:
                QMessageBox.critical(self, "Ошибка", result["error"])

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)