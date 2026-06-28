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
    """
    print(f"\n{'=' * 60}")
    print(f"🔍 НАЧАЛО ПОИСКА ФОТО")
    print(f"{'=' * 60}")
    print(f" Входные данные:")
    print(f"   Гос. номер: '{license_plate}'")
    print(f"   Марка: '{brand}'")
    print(f"   Модель: '{model}'")

    images_dir = get_images_dir()
    print(f"📁 Путь к папке images: {images_dir}")
    print(f"📁 Папка существует: {images_dir.exists()}")

    if not images_dir.exists():
        print(f"❌ Папка images не найдена!")
        return None

    # Список всех файлов в папке
    all_files = list(images_dir.iterdir())
    print(f"📄 Всего файлов в папке: {len(all_files)}")

    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

    # Показываем все доступные фото
    print(f"\n📸 Доступные фото:")
    for f in all_files:
        if f.suffix.lower() in extensions:
            print(f"   - {f.name} (stem: '{f.stem}', stem.upper: '{f.stem.upper()}')")

    # 1. Ищем по гос. номеру
    if license_plate:
        print(f"\n🔎 ШАГ 1: Поиск по гос. номеру '{license_plate}'")
        plate_clean = license_plate.replace(' ', '').upper()
        print(f"   Очищенный номер: '{plate_clean}'")

        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '')
                print(f"   Сравниваем: '{file_name_upper}' == '{plate_clean}' -> {file_name_upper == plate_clean}")

                if file_name_upper == plate_clean:
                    print(f"   ✅ НАЙДЕНО: {file_path}")
                    return str(file_path)

        print(f"   ❌ По гос. номеру не найдено")

    # 2. Ищем по марке и модели
    if brand and model:
        print(f"\n🔎 ШАГ 2: Поиск по марке+модели '{brand} {model}'")
        brand_model = f"{brand}_{model}".replace(' ', '_').upper()
        brand_model2 = f"{brand}{model}".replace(' ', '').upper()
        print(f"   Вариант 1: '{brand_model}'")
        print(f"   Вариант 2: '{brand_model2}'")

        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '_')
                file_name_upper2 = file_path.stem.upper().replace(' ', '')

                match1 = file_name_upper == brand_model
                match2 = file_name_upper2 == brand_model2

                print(f"   Сравниваем: '{file_name_upper}' == '{brand_model}' -> {match1}")
                print(f"   Сравниваем: '{file_name_upper2}' == '{brand_model2}' -> {match2}")

                if match1 or match2:
                    print(f"   ✅ НАЙДЕНО: {file_path}")
                    return str(file_path)

        print(f"   ❌ По марке+модели не найдено")

    # 3. Ищем только по марке
    if brand:
        print(f"\n🔎 ШАГ 3: Поиск только по марке '{brand}'")
        brand_clean = brand.replace(' ', '_').upper()
        print(f"   Очищенная марка: '{brand_clean}'")

        for file_path in images_dir.iterdir():
            if file_path.suffix.lower() in extensions:
                file_name_upper = file_path.stem.upper().replace(' ', '_')
                print(f"   Сравниваем: '{file_name_upper}' == '{brand_clean}' -> {file_name_upper == brand_clean}")

                if file_name_upper == brand_clean:
                    print(f"   ✅ НАЙДЕНО: {file_path}")
                    return str(file_path)

        print(f"   ❌ По марке не найдено")

    print(f"\n❌ ФОТО НЕ НАЙДЕНО")
    print(f"{'=' * 60}\n")
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