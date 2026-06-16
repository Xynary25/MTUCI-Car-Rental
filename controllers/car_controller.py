from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.car import Car
from typing import List, Dict, Any
from utils.system_utils import log_action
from models.audit_log import ActionType
from utils.image_utils import find_car_image

class CarController:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_cars(self) -> List[Dict[str, Any]]:
        """Получение списка всех автомобилей."""
        cars = self.db.query(Car).all()
        return [
            {
                "id": c.id,
                "brand": c.brand,
                "model": c.model,
                "license_plate": c.license_plate,
                "year": c.year,
                "transmission": c.transmission,
                "fuel_type": c.fuel_type,
                "engine_volume": c.engine_volume,
                "engine_power": c.engine_power,
                "color": c.color,
                "body_type": c.body_type,
                "seats": c.seats,
                "daily_rate": c.daily_rate,
                "description": c.description,
                "image_path": c.image_path,
                "is_available": bool(c.is_available),
                "created_at": c.created_at
            }
            for c in cars
        ]

    def add_car(self, data: dict) -> Dict[str, Any]:
        """Добавление нового автомобиля со ВСЕМИ полями."""
        if not data.get("brand") or not data.get("model") or not data.get("license_plate") or data.get("daily_rate",
                                                                                                       0) <= 0:
            return {"success": False, "error": "Марка, модель, гос. номер обязательны, а ставка должна быть > 0"}

        # === УМНАЯ ЗАГРУЗКА ФОТО ===
        image_path = data.get("image_path")
        if not image_path:
            # Пытаемся найти фото автоматически
            image_path = find_car_image(
                license_plate=data.get("license_plate"),
                brand=data.get("brand"),
                model=data.get("model")
            )

        new_car = Car(
            brand=data["brand"].strip(),
            model=data["model"].strip(),
            license_plate=data["license_plate"].strip().upper(),
            year=data.get("year", 2024),
            transmission=data.get("transmission", "Автомат"),
            fuel_type=data.get("fuel_type", "Бензин"),
            engine_volume=data.get("engine_volume", ""),
            engine_power=data.get("engine_power", 0),
            color=data.get("color", ""),
            body_type=data.get("body_type", "Седан"),
            seats=data.get("seats", 5),
            daily_rate=data["daily_rate"],
            description=data.get("description", ""),
            image_path=data.get("image_path"),
            is_available=data.get("is_available", True)
        )
        try:
            self.db.add(new_car)
            self.db.commit()
            self.db.refresh(new_car)

            # ЛОГИРОВАНИЕ: Добавление автомобиля
            log_action(
                db=self.db,
                action_type=ActionType.CREATE,
                entity_name="Car",
                description=f"Добавлен автомобиль {new_car.brand} {new_car.model} ({new_car.license_plate})",
                entity_id=new_car.id,
                user_info="Admin"
            )

            return {"success": True, "data": new_car}
        except IntegrityError:
            self.db.rollback()
            return {"success": False, "error": "Автомобиль с таким гос. номером уже существует"}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка БД: {str(e)}"}

    def update_car(self, car_id: int, data: dict) -> Dict[str, Any]:
        """Обновление автомобиля со ВСЕМИ полями, включая image_path."""
        car = self.db.query(Car).filter(Car.id == car_id).first()
        if not car:
            return {"success": False, "error": "Автомобиль не найден"}

        # Сохраняем старые значения для логирования
        old_brand = car.brand
        old_model = car.model
        old_plate = car.license_plate

        car.brand = data["brand"].strip()
        car.model = data["model"].strip()
        car.license_plate = data["license_plate"].strip().upper()
        car.year = data.get("year", car.year)
        car.transmission = data.get("transmission", car.transmission)
        car.fuel_type = data.get("fuel_type", car.fuel_type)
        car.engine_volume = data.get("engine_volume", car.engine_volume)
        car.engine_power = data.get("engine_power", car.engine_power)
        car.color = data.get("color", car.color)
        car.body_type = data.get("body_type", car.body_type)
        car.seats = data.get("seats", car.seats)
        car.daily_rate = data["daily_rate"]
        car.description = data.get("description", car.description)
        car.image_path = data.get("image_path", car.image_path)
        car.is_available = bool(data.get("is_available", car.is_available))

        try:
            self.db.commit()

            # ЛОГИРОВАНИЕ: Обновление автомобиля
            log_action(
                db=self.db,
                action_type=ActionType.UPDATE,
                entity_name="Car",
                description=f"Обновлён автомобиль {car.brand} {car.model} ({car.license_plate})",
                entity_id=car.id,
                user_info="Admin"
            )

            return {"success": True}
        except IntegrityError:
            self.db.rollback()
            return {"success": False, "error": "Автомобиль с таким гос. номером уже существует"}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка при обновлении: {str(e)}"}

    def delete_car(self, car_id: int) -> Dict[str, Any]:
        car = self.db.query(Car).filter(Car.id == car_id).first()
        if not car:
            return {"success": False, "error": "Автомобиль не найден"}

        car_info = f"{car.brand} {car.model} ({car.license_plate})"

        try:
            self.db.delete(car)
            self.db.commit()

            # ЛОГИРОВАНИЕ: Удаление автомобиля
            log_action(
                db=self.db,
                action_type=ActionType.DELETE,
                entity_name="Car",
                description=f"Удалён автомобиль {car_info}",
                entity_id=car_id,
                user_info="Admin"
            )

            return {"success": True}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Ошибка при удалении: {str(e)}"}