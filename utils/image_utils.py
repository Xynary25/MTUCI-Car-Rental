"""
Утилиты для работы с изображениями автомобилей.
Автоматический поиск фото по гос. номеру или марке/модели.
"""
import os
from pathlib import Path


def get_images_dir() -> Path:
    """Возвращает путь к папке images."""
    base_dir = Path(__file__).parent.parent
    images_dir = base_dir / "images"
    images_dir.mkdir(exist_ok=True)  # Создаем папку если нет
    return images_dir


def find_car_image(license_plate: str = None, brand: str = None, model: str = None) -> str:
    """
    Автоматический поиск фотографии автомобиля (CASE-INSENSITIVE).

    Приоритет поиска:
    1. По гос. номеру (например, А777АА777.jpg)
    2. По марке и модели (например, Toyota_Camry.jpg)
    3. Только по марке (например, Toyota.jpg)

    Args:
        license_plate: Гос. номер автомобиля
        brand: Марка автомобиля
        model: Модель автомобиля

    Returns:
        Полный путь к файлу изображения или None если не найдено
    """
    images_dir = get_images_dir()

    # Поддерживаемые расширения
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

    # 1. Ищем по гос. номеру (приоритет) - CASE INSENSITIVE
    if license_plate:
        # Убираем пробелы и приводим к верхнему регистру для поиска
        plate_clean = license_plate.replace(' ', '').upper()
        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                # Сравниваем без расширения и без учета регистра
                file_name_upper = file_path.stem.upper().replace(' ', '')
                if file_name_upper == plate_clean:
                    return str(file_path)

    # 2. Ищем по марке и модели - CASE INSENSITIVE
    if brand and model:
        brand_model = f"{brand}_{model}".replace(' ', '_').upper()
        brand_model2 = f"{brand}{model}".replace(' ', '').upper()

        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '_')
                file_name_upper2 = file_path.stem.upper().replace(' ', '')

                if file_name_upper == brand_model or file_name_upper2 == brand_model2:
                    return str(file_path)

    # 3. Ищем только по марке - CASE INSENSITIVE
    if brand:
        brand_clean = brand.replace(' ', '_').upper()
        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '_')
                if file_name_upper == brand_clean:
                    return str(file_path)

    return None


def get_available_images() -> list:
    """
    Возвращает список всех доступных изображений в папке images.

    Returns:
        Список кортежей (имя_файла, полный_путь)
    """
    images_dir = get_images_dir()
    extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')

    images = []
    for file_path in images_dir.iterdir():
        if file_path.suffix.lower() in extensions:
            images.append((file_path.name, str(file_path)))

    return sorted(images)


def save_uploaded_image(source_path: str, license_plate: str = None,
                       brand: str = None, model: str = None) -> str:
    """
    Сохраняет загруженное изображение в папку images с правильным именем.

    Args:
        source_path: Путь к исходному файлу
        license_plate: Гос. номер (для имени файла)
        brand: Марка автомобиля
        model: Модель автомобиля

    Returns:
        Путь к сохраненному файлу
    """
    images_dir = get_images_dir()

    # Определяем имя файла
    if license_plate:
        filename = license_plate.replace(' ', '').upper()
    elif brand and model:
        filename = f"{brand}_{model}".replace(' ', '_')
    else:
        filename = "car_image"

    # Определяем расширение
    ext = Path(source_path).suffix.lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
        ext = '.jpg'

    # Полный путь
    dest_path = images_dir / f"{filename}{ext}"

    # Копируем файл
    import shutil
    shutil.copy2(source_path, dest_path)

    return str(dest_path)