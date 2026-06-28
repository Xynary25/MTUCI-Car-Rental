"""
Утилиты для конвертации путей между веб-порталом и десктопной СУ.
"""
import os
from pathlib import Path

def get_project_root() -> Path:
    """Возвращает корневую папку проекта."""
    return Path(__file__).parent.parent

def get_images_dir() -> Path:
    """Возвращает путь к папке images (десктопная СУ)."""
    return get_project_root() / "images"

def url_path_to_absolute(url_path: str) -> str:
    """
    Конвертирует URL-путь (например, /static/car_images/photo.jpg)
    в абсолютный путь к файлу на диске.

    Args:
        url_path: URL-путь (например, '/static/car_images/car_1.jpg')

    Returns:
        Абсолютный путь к файлу
    """
    if not url_path:
        return ""

    # Если путь уже абсолютный и файл существует - возвращаем как есть
    if os.path.isabs(url_path) and os.path.exists(url_path):
        return url_path

    project_root = get_project_root()

    # Если это путь из веб-портала (/static/car_images/...)
    if url_path.startswith('/static/car_images/'):
        # Ищем файл в папке images/ десктопной СУ
        filename = url_path.split('/')[-1]
        images_dir = get_images_dir()
        absolute_path = images_dir / filename

        if absolute_path.exists():
            return str(absolute_path)

        # Если не нашли в images/, пробуем в static/car_images/
        static_path = project_root / "static" / "car_images" / filename
        if static_path.exists():
            return str(static_path)

        return str(absolute_path)  # Возвращаем путь даже если файл не найден

    # Если это путь из папки images/
    if url_path.startswith('/images/'):
        relative_path = url_path.lstrip('/')
        absolute_path = project_root / relative_path
        return str(absolute_path)

    # Если это относительный путь
    if not url_path.startswith('/'):
        absolute_path = project_root / url_path
        return str(absolute_path)

    return url_path

def file_exists(url_path: str) -> bool:
    """
    Проверяет существование файла по URL-пути.
    """
    if not url_path:
        return False

    absolute_path = url_path_to_absolute(url_path)
    return os.path.exists(absolute_path)

def find_image_in_images_dir(license_plate: str = None, brand: str = None, model: str = None) -> str:
    """
    Поиск фото в папке images/ по гос. номеру или марке/модели.
    Возвращает абсолютный путь к файлу.
    """
    images_dir = get_images_dir()
    if not images_dir.exists():
        return None

    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

    # 1. Ищем по гос. номеру
    if license_plate:
        plate_clean = license_plate.replace(' ', '').upper()
        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '')
                if file_name_upper == plate_clean:
                    return str(file_path)

    # 2. Ищем по марке и модели
    if brand and model:
        brand_model = f"{brand}_{model}".replace(' ', '_').upper()
        brand_model2 = f"{brand}{model}".replace(' ', '').upper()

        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '_')
                file_name_upper2 = file_path.stem.upper().replace(' ', '')

                if file_name_upper == brand_model or file_name_upper2 == brand_model2:
                    return str(file_path)

    # 3. Ищем только по марке
    if brand:
        brand_clean = brand.replace(' ', '_').upper()
        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '_')
                if file_name_upper == brand_clean:
                    return str(file_path)

    return None