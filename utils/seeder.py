from sqlalchemy.orm import Session
from datetime import date, timedelta
from models.car import Car
from models.client import Client
from models.agreement import RentalAgreement, AgreementStatus
from models.payment import Payment, PaymentStatus, PaymentMethod
from models.expense import Expense, ExpenseType
from models.penalty import Penalty, PenaltyType, PenaltyStatus
from models.maintenance import Maintenance, MaintenanceType, MaintenanceStatus
from utils.logger import app_logger
import os


def seed_database(db: Session):
    """Наполнение базы данных расширенными реалистичными данными."""
    app_logger.info("Начало проверки и наполнения базы данных (Seeding)...")

    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    today = date.today()  # ← ПЕРЕНЕСЕНО В НАЧАЛО ФУНКЦИИ!

    if db.query(Car).count() == 0:
        cars_data = [
            {
                "brand": "Toyota", "model": "Camry", "license_plate": "А777АА777",
                "year": 2022, "transmission": "Автомат", "fuel_type": "Бензин",
                "engine_volume": "2.5 л", "engine_power": 200, "color": "Белый перламутр",
                "body_type": "Седан", "seats": 5, "daily_rate": 3500,
                "is_available": True,
                "description": "Комфортный бизнес-седан с автоматической коробкой передач. Идеален для деловых поездок."
            },
            {
                "brand": "Hyundai", "model": "Solaris", "license_plate": "В123ОР77",
                "year": 2021, "transmission": "Механика", "fuel_type": "Бензин",
                "engine_volume": "1.6 л", "engine_power": 123, "color": "Черный металлик",
                "body_type": "Седан", "seats": 5, "daily_rate": 2000,
                "is_available": True,
                "description": "Надежный и экономичный автомобиль для города. Низкий расход топлива."
            },
            {
                "brand": "Kia", "model": "K5", "license_plate": "Е456КХ99",
                "year": 2023, "transmission": "Автомат", "fuel_type": "Бензин",
                "engine_volume": "2.0 л", "engine_power": 150, "color": "Синий металлик",
                "body_type": "Седан", "seats": 5, "daily_rate": 3200,
                "is_available": False,
                "description": "Современный седан с богатым оснащением и стильным дизайном."
            },
            {
                "brand": "BMW", "model": "X5", "license_plate": "М888ММ777",
                "year": 2023, "transmission": "Автомат", "fuel_type": "Дизель",
                "engine_volume": "3.0 л", "engine_power": 286, "color": "Черный сапфир",
                "body_type": "Внедорожник", "seats": 7, "daily_rate": 8500,
                "is_available": True,
                "description": "Премиальный внедорожник с полным приводом xDrive. Максимальный комфорт и безопасность."
            },
            {
                "brand": "Mercedes-Benz", "model": "E-Class", "license_plate": "К999КК99",
                "year": 2022, "transmission": "Автомат", "fuel_type": "Бензин",
                "engine_volume": "2.0 л", "engine_power": 197, "color": "Серебристый иридий",
                "body_type": "Седан", "seats": 5, "daily_rate": 7500,
                "is_available": True,
                "description": "Бизнес-класс с максимальным комфортом. Системы помощи водителю."
            },
            {
                "brand": "Volkswagen", "model": "Tiguan", "license_plate": "Н555НН77",
                "year": 2021, "transmission": "Робот", "fuel_type": "Бензин",
                "engine_volume": "2.0 л", "engine_power": 180, "color": "Белый чистый",
                "body_type": "Кроссовер", "seats": 5, "daily_rate": 4500,
                "is_available": True,
                "description": "Популярный семейный кроссовер с просторным салоном и багажником."
            },
            {
                "brand": "Lexus", "model": "RX", "license_plate": "Р111РР99",
                "year": 2023, "transmission": "Автомат", "fuel_type": "Гибрид",
                "engine_volume": "3.5 л", "engine_power": 313, "color": "Бежевый перламутр",
                "body_type": "Кроссовер", "seats": 5, "daily_rate": 9500,
                "is_available": True,
                "description": "Люксовый гибридный кроссовер. Тихий, мощный и экономичный."
            },
            {
                "brand": "Skoda", "model": "Octavia", "license_plate": "Т222ТТ77",
                "year": 2020, "transmission": "Механика", "fuel_type": "Дизель",
                "engine_volume": "2.0 л", "engine_power": 150, "color": "Серый кварц",
                "body_type": "Универсал", "seats": 5, "daily_rate": 3000,
                "is_available": True,
                "description": "Практичный универсал с огромным багажником. Идеален для путешествий."
            },
            {
                "brand": "Mazda", "model": "CX-5", "license_plate": "У333УУ99",
                "year": 2022, "transmission": "Автомат", "fuel_type": "Бензин",
                "engine_volume": "2.5 л", "engine_power": 194, "color": "Красный металлик",
                "body_type": "Кроссовер", "seats": 5, "daily_rate": 4200,
                "is_available": True,
                "description": "Стильный кроссовер с отличным управлением и спортивным характером."
            },
            {
                "brand": "Kia", "model": "Carnival", "license_plate": "Ф444ФФ77",
                "year": 2023, "transmission": "Автомат", "fuel_type": "Дизель",
                "engine_volume": "2.2 л", "engine_power": 199, "color": "Белый снежный",
                "body_type": "Минивэн", "seats": 9, "daily_rate": 6500,
                "is_available": True,
                "description": "Просторный 9-местный минивэн для большой семьи или группы. Три ряда сидений."
            },
            {
                "brand": "Audi", "model": "Q7", "license_plate": "Х666ХХ99",
                "year": 2023, "transmission": "Автомат", "fuel_type": "Дизель",
                "engine_volume": "3.0 л", "engine_power": 249, "color": "Черный миф",
                "body_type": "Внедорожник", "seats": 7, "daily_rate": 10000,
                "is_available": True,
                "description": "Полноразмерный премиум внедорожник. Quattro, виртуальная приборная панель."
            },
            {
                "brand": "Tesla", "model": "Model 3", "license_plate": "Ц777ЦЦ77",
                "year": 2023, "transmission": "Автомат", "fuel_type": "Электро",
                "engine_volume": "—", "engine_power": 283, "color": "Белый перламутр",
                "body_type": "Седан", "seats": 5, "daily_rate": 7000,
                "is_available": True,
                "description": "Электромобиль с автопилотом. Запас хода до 500 км. Быстрая зарядка."
            },
        ]
        for c_data in cars_data:
            db.add(Car(**c_data))
        db.commit()
        app_logger.info(f"Добавлено {len(cars_data)} автомобилей.")

    if db.query(Client).count() == 0:
        clients_data = [
            {"full_name": "Иванов Иван Иванович", "passport_series": "4515", "passport_number": "123456",
             "phone": "+79001112233", "email": "ivanov@test.ru"},
            {"full_name": "Петрова Анна Сергеевна", "passport_series": "4610", "passport_number": "654321",
             "phone": "+79004445566", "email": "petrova@test.ru"},
            {"full_name": "Сидоров Петр Александрович", "passport_series": "4512", "passport_number": "789012",
             "phone": "+79007778899", "email": "sidorov@test.ru"},
            {"full_name": "Козлова Елена Дмитриевна", "passport_series": "4615", "passport_number": "345678",
             "phone": "+79001239876", "email": "kozlova@test.ru"},
            {"full_name": "Новиков Максим Игоревич", "passport_series": "4518", "passport_number": "901234",
             "phone": "+79005554433", "email": "novikov@test.ru"},
            {"full_name": "Морозова Ольга Владимировна", "passport_series": "4620", "passport_number": "567890",
             "phone": "+79006667788", "email": "morozova@test.ru"},
            {"full_name": "Волков Андрей Сергеевич", "passport_series": "4522", "passport_number": "234567",
             "phone": "+79009998877", "email": "volkov@test.ru"},
            {"full_name": "Лебедева Мария Павловна", "passport_series": "4625", "passport_number": "890123",
             "phone": "+79002223344", "email": "lebedeva@test.ru"},
        ]
        for cl_data in clients_data:
            db.add(Client(**cl_data))
        db.commit()
        app_logger.info(f"Добавлено {len(clients_data)} клиентов.")

    if db.query(RentalAgreement).count() == 0:
        client2 = db.query(Client).filter(Client.full_name == "Петрова Анна Сергеевна").first()
        client3 = db.query(Client).filter(Client.full_name == "Сидоров Петр Александрович").first()
        car1 = db.query(Car).filter(Car.license_plate == "А777АА777").first()
        car3 = db.query(Car).filter(Car.license_plate == "Е456КХ99").first()

        # Активный договор на Kia K5 (машина НЕ доступна)
        agreement1 = RentalAgreement(
            client_id=client2.id,
            car_id=car3.id,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=5),
            total_cost=3200 * 7,
            status=AgreementStatus.ACTIVE
        )
        db.add(agreement1)
        db.commit()

        db.add(Payment(
            agreement_id=agreement1.id,
            amount=agreement1.total_cost,
            payment_date=today - timedelta(days=2),
            method=PaymentMethod.CARD,
            status=PaymentStatus.PAID
        ))
        db.commit()

        # Завершенный договор
        agreement2 = RentalAgreement(
            client_id=client3.id,
            car_id=car1.id,
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=7),
            total_cost=3500 * 3,
            status=AgreementStatus.COMPLETED
        )
        db.add(agreement2)
        db.commit()

        db.add(Payment(
            agreement_id=agreement2.id,
            amount=agreement2.total_cost,
            payment_date=today - timedelta(days=10),
            method=PaymentMethod.CASH,
            status=PaymentStatus.PAID
        ))
        db.commit()
        app_logger.info("Добавлены договоры аренды.")

    if db.query(Expense).count() == 0:
        car1 = db.query(Car).filter(Car.license_plate == "А777АА777").first()
        car4 = db.query(Car).filter(Car.license_plate == "М888ММ777").first()

        db.add(Expense(
            car_id=car1.id,
            expense_type=ExpenseType.REPAIR,
            amount=15000,
            description="Замена масла и фильтров",
            date=today - timedelta(days=5)
        ))
        db.add(Expense(
            car_id=car4.id,
            expense_type=ExpenseType.INSURANCE,
            amount=85000,
            description="КАСКО на год",
            date=today - timedelta(days=20)
        ))
        db.add(Expense(
            expense_type=ExpenseType.OTHER,
            amount=5000,
            description="Аренда офиса",
            date=today - timedelta(days=1)
        ))
        db.commit()
        app_logger.info("Добавлены расходы.")

    # Добавление тестовых штрафов
    if db.query(Penalty).count() == 0:
        active_agreement = db.query(RentalAgreement).filter(
            RentalAgreement.status == AgreementStatus.ACTIVE
        ).first()

        completed_agreement = db.query(RentalAgreement).filter(
            RentalAgreement.status == AgreementStatus.COMPLETED
        ).first()

        if active_agreement:
            db.add(Penalty(
                agreement_id=active_agreement.id,
                penalty_type=PenaltyType.DAMAGE,
                amount=25000,
                description="Царапина на заднем бампере",
                date=today - timedelta(days=1),
                is_paid=False,
                status=PenaltyStatus.PENDING
            ))
            db.add(Penalty(
                agreement_id=active_agreement.id,
                penalty_type=PenaltyType.SMOKING,
                amount=5000,
                description="Следы курения в салоне",
                date=today,
                is_paid=False,
                status=PenaltyStatus.PENDING
            ))

        if completed_agreement:
            db.add(Penalty(
                agreement_id=completed_agreement.id,
                penalty_type=PenaltyType.LATE_RETURN,
                amount=3500,
                description="Возврат на 5 часов позже срока",
                date=today - timedelta(days=7),
                is_paid=True,
                status=PenaltyStatus.PAID
            ))
            db.add(Penalty(
                agreement_id=completed_agreement.id,
                penalty_type=PenaltyType.CLEANING,
                amount=2000,
                description="Мойка после аренды (отменено клиентом)",
                date=today - timedelta(days=8),
                is_paid=False,
                status=PenaltyStatus.CANCELLED
            ))

        db.commit()
        app_logger.info("Добавлены тестовые штрафы.")

    if db.query(Maintenance).count() == 0:
        cars = db.query(Car).all()

        if len(cars) >= 2:
            db.add(Maintenance(
                car_id=cars[0].id,
                maintenance_type=MaintenanceType.PLANNED,
                description="Плановое ТО-2: замена масла, фильтров, проверка тормозов",
                mileage=45000,
                next_mileage=55000,
                maintenance_date=today - timedelta(days=30),
                next_maintenance_date=today + timedelta(days=15),
                cost=15000,
                status=MaintenanceStatus.COMPLETED,
                performed_by="СТО АвтоСервис"
            ))

            db.add(Maintenance(
                car_id=cars[1].id,
                maintenance_type=MaintenanceType.SEASONAL,
                description="Сезонная замена шин с летних на зимние",
                mileage=32000,
                next_mileage=None,
                maintenance_date=today,
                next_maintenance_date=today + timedelta(days=180),
                cost=8000,
                status=MaintenanceStatus.SCHEDULED,
                performed_by="Шиномонтаж Профи"
            ))

            if len(cars) >= 3:
                db.add(Maintenance(
                    car_id=cars[2].id,
                    maintenance_type=MaintenanceType.UNSCHEDULED,
                    description="Замена тормозных колодок (внепланово)",
                    mileage=28000,
                    next_mileage=None,
                    maintenance_date=today - timedelta(days=10),
                    next_maintenance_date=None,
                    cost=12000,
                    status=MaintenanceStatus.COMPLETED,
                    performed_by="СТО АвтоСервис"
                ))

        db.commit()
        app_logger.info("Добавлены тестовые записи ТО.")

    app_logger.info("Наполнение базы данных успешно завершено.")