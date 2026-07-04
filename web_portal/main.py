import hashlib
import secrets
from datetime import date, datetime
from sqlite3 import IntegrityError
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Form, Cookie, Request, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy import func
from sqlalchemy.orm import Session
from urllib.parse import quote, unquote
from database import get_db, init_db
from models.support_message import SupportMessage
from utils.dev_console import log_error
from utils.notification_service import NotificationService
from utils.logger import app_logger, log_security_event, log_user_action
from web_models import Car, Client, RentalAgreement, Penalty, User, UserRole, AgreementStatus, PenaltyType, \
    PenaltyStatus
import uvicorn
import os
from pathlib import Path
import shutil
import uuid
from return_request import ReturnRequest, ReturnRequestStatus
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_portal.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ДрайвКонтроль - Управление Автопрокатом",
    version="0.1.0",
    openapi_version="3.0.3",
    openapi_url="/openapi.json"
)
templates = Jinja2Templates(directory="templates")

# Путь к корню проекта
PROJECT_ROOT = Path(__file__).parent.parent

# Настройки для загрузки фото
UPLOAD_DIR = Path("static/car_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

SUPPORT_ATTACHMENTS_DIR = Path("static/support_attachments")
SUPPORT_ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/support_attachments", StaticFiles(directory=str(SUPPORT_ATTACHMENTS_DIR)), name="support_attachments")
print(f"📎 Папка прикреплённых файлов подключена: {SUPPORT_ATTACHMENTS_DIR}")

# Монтируем папку images из десктопной СУ
IMAGES_DIR = PROJECT_ROOT / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")
    print(f"📸 Папка изображений СУ подключена: {IMAGES_DIR}")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Кастомизация OpenAPI схемы
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    # Исправляем ошибки с contentMediaType
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]
        for schema_name, schema in schemas.items():
            if "properties" in schema:
                for prop_name, prop in schema["properties"].items():
                    # Для файловых полей
                    if isinstance(prop, dict) and "contentMediaType" in prop:
                        del prop["contentMediaType"]
                        prop["format"] = "binary"
                    # Для массивов файлов
                    if isinstance(prop, dict) and "items" in prop:
                        if isinstance(prop["items"], dict) and "contentMediaType" in prop["items"]:
                            del prop["items"]["contentMediaType"]
                            prop["items"]["format"] = "binary"

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi

def allowed_file(filename):
    """Проверка расширения файла."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file: UploadFile, car_id: int) -> str:
    """Сохранение загруженного файла и возврат пути."""
    ext = file.filename.split('.')[-1] if file.filename else 'jpg'
    filename = f"car_{car_id}_{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/static/car_images/{filename}"


def get_car_image_url(car) -> str:
    """
    Получение URL изображения автомобиля.
    Обрабатывает пути из десктопной СУ, внешние URL и локальные файлы.
    """
    if not car.image_path:
        return "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600&auto=format&fit=crop&q=80"

    image_path = car.image_path.strip()

    # Если это путь из десктопной СУ (images/...)
    if image_path.startswith("images/"):
        return "/" + image_path

    # Если это внешний URL
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path

    # Если это локальный путь из static
    if image_path.startswith("/static/") or image_path.startswith("static/"):
        return "/" + image_path if not image_path.startswith("/") else image_path

    # Если это относительный путь
    if not image_path.startswith("/"):
        return "/" + image_path

    # Дефолтное изображение
    return "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600&auto=format&fit=crop&q=80"


def sync_car_photos():
    """Синхронизация фото между папками images/ и static/car_images/"""
    import shutil
    from pathlib import Path

    images_dir = PROJECT_ROOT / "images"
    web_images_dir = UPLOAD_DIR

    images_dir.mkdir(parents=True, exist_ok=True)
    web_images_dir.mkdir(parents=True, exist_ok=True)

    # Копируем из images/ в static/car_images/
    for src_file in images_dir.glob("*"):
        if src_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            dst_file = web_images_dir / src_file.name
            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"✅ Скопировано: {src_file.name}")

    # Копируем из static/car_images/ в images/
    for src_file in web_images_dir.glob("*"):
        if src_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            dst_file = images_dir / src_file.name
            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"✅ Скопировано: {src_file.name}")

def get_car_status_text(car, db: Session) -> str:
    """Определение текстового статуса автомобиля."""
    if car.is_available:
        return "available"

    # Проверяем есть ли активная аренда
    active_rental = db.query(RentalAgreement).filter(
        RentalAgreement.car_id == car.id,
        RentalAgreement.status == AgreementStatus.ACTIVE
    ).first()

    if active_rental:
        return "rented"
    else:
        return "maintenance"


# Инициализация БД при старте
init_db()
# Синхронизация фото
sync_car_photos()
print("📊 База данных подключена")


@app.get("/", response_class=HTMLResponse)
def read_root(
        request: Request,
        user_role: str = Cookie(default=None),
        user_id: str = Cookie(default=None),
        user_name: str = Cookie(default=None),
        db: Session = Depends(get_db)
):
    """Главная страница сайта."""
    if not user_role:
        return RedirectResponse(url="/login", status_code=303)

    cars = db.query(Car).all()
    agreements = db.query(RentalAgreement).all()

    # Статистика
    stats = None
    if user_role == "admin":
        total_revenue = sum(a.total_cost for a in agreements) if agreements else 0
        active_rentals = db.query(RentalAgreement).filter(
            RentalAgreement.status == AgreementStatus.ACTIVE
        ).count()
        total_cars = db.query(Car).count()
        available_cars = db.query(Car).filter(Car.is_available == True).count()
        rented_cars = total_cars - available_cars
        fleet_load = round((rented_cars / total_cars) * 100) if total_cars > 0 else 0

        stats = {
            "total_revenue": int(total_revenue),
            "active_rentals": active_rentals,
            "fleet_load": fleet_load
        }

    # Формируем данные аренд для UI
    agreements_ui = []
    for a in agreements:
        client = db.query(Client).filter(Client.id == a.client_id).first()
        car = db.query(Car).filter(Car.id == a.car_id).first()
        penalties = db.query(Penalty).filter(Penalty.agreement_id == a.id).all()

        today = date.today()
        overdue_days = 0
        if a.status == AgreementStatus.ACTIVE and a.end_date and today > a.end_date:
            overdue_days = (today - a.end_date).days

        # Для клиента показываем только его аренды
        if user_role == "client" and client and client.id != int(user_id):
            continue

        # Формируем штрафы с правильным извлечением Enum значений
        fines_data = []
        for p in penalties:
            penalty_type_value = p.penalty_type.value if hasattr(p.penalty_type, 'value') else str(p.penalty_type)
            is_paid = p.is_paid if hasattr(p, 'is_paid') else False

            fines_data.append({
                "id": p.id,
                "amount": p.amount,
                "penalty_type": penalty_type_value,
                "description": p.description or "",
                "is_paid": is_paid
            })

        agreements_ui.append({
            "id": a.id,
            "client_name": client.full_name if client else "Неизвестно",
            "car_info": f"{car.brand} {car.model}" if car else "Неизвестно",
            "period": f"{a.start_date.strftime('%d.%m.%Y')} — {a.end_date.strftime('%d.%m.%Y')}" if a.start_date and a.end_date else "—",
            "total_price": a.total_cost,
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
            "overdue_days": overdue_days,
            "fines": fines_data
        })

    # Имя пользователя
    if user_role == "admin":
        display_name = "Администратор"
    elif user_name:
        display_name = unquote(user_name)
    else:
        client = db.query(Client).filter(Client.id == int(user_id) if user_id else 0).first()
        display_name = client.full_name if client else "Клиент"

    # Добавляем URL изображений и статусы для каждой машины
    cars_with_images = []
    for car in cars:
        car_status = get_car_status_text(car, db)
        car_dict = {
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "year": car.year,
            "transmission": car.transmission,
            "fuel_type": car.fuel_type,
            "color": car.color,
            "body_type": car.body_type,
            "seats": car.seats,
            "daily_rate": car.daily_rate,
            "description": car.description,
            "is_available": car.is_available,
            "image_url": get_car_image_url(car),
            "license_plate": car.license_plate,
            "status_text": car_status
        }
        cars_with_images.append(car_dict)

    # Проверяем есть ли pending запросы на возврат для каждого rental
    for rental in agreements_ui:
        if rental['status'] == 'active':
            pending_request = db.query(ReturnRequest).filter(
                ReturnRequest.rental_id == rental['id'],
                ReturnRequest.status == ReturnRequestStatus.PENDING
            ).first()
            rental['has_pending_return'] = pending_request is not None

    # Считаем непрочитанные уведомления для админа
    admin_unread_count = 0
    if user_role == "admin":
        from models.notification import Notification
        admin_unread_count = db.query(Notification).filter(
            Notification.is_read == False,
            (Notification.user_id == None) | (Notification.user_id == int(user_id))
        ).count()

    # Получаем уведомления для пользователя
    user_notifications = []
    admin_unread_count = 0

    if user_role == "client":
        # Для клиента - только его уведомления
        from models.notification import Notification
        user_notifications = db.query(Notification).filter(
            Notification.user_id == int(user_id)
        ).order_by(Notification.created_at.desc()).limit(10).all()
    elif user_role == "admin":
        # Для админа - все уведомления + счетчик непрочитанных
        from models.notification import Notification
        admin_unread_count = db.query(Notification).filter(
            Notification.is_read == False,
            (Notification.user_id == None) | (Notification.user_id == int(user_id))
        ).count()
        user_notifications = db.query(Notification).filter(
            (Notification.user_id == None) | (Notification.user_id == int(user_id))
        ).order_by(Notification.created_at.desc()).limit(10).all()

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "cars": cars_with_images,
            "rentals": agreements_ui,
            "stats": stats,
            "role": user_role,
            "current_user": display_name,
            "current_user_id": user_id,
            "user_notifications": user_notifications,
            "admin_unread_count": admin_unread_count,
        }
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = None):
    """Страница входа в систему."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {"show_login": True, "error": error}
    )


@app.post("/auth/login")
def process_login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """Обработка входа в систему."""
    app_logger.info(f"🔐 Попытка входа: username={username}")
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            app_logger.warning(f"❌ Пользователь не найден: {username}")
            return RedirectResponse(
                url="/login?error=❌ Пользователь не найден",
                status_code=303
            )

        if not user.check_password(password):
            app_logger.warning(f"❌ Неверный пароль для: {username}")
            return RedirectResponse(
                url="/login?error=❌ Неверный пароль",
                status_code=303
            )

        if not user.is_active:
            app_logger.warning(f"❌ Аккаунт заблокирован: {username}")
            return RedirectResponse(
                url="/login?error=❌ Аккаунт заблокирован",
                status_code=303
            )

        # Для админов
        if user.role.value in ["admin", "superadmin", "manager"]:
            app_logger.info(f"✅ Вход админа: {username} ({user.role.value})")
            response = RedirectResponse(url="/", status_code=303)
            response.set_cookie(key="user_role", value="admin", max_age=86400)
            response.set_cookie(key="user_id", value=str(user.id), max_age=86400)
            response.delete_cookie("user_name")
            return response

        # Для клиентов - ищем по email, затем по ID
        client = None
        if user.email:
            client = db.query(Client).filter(Client.email == user.email).first()
        if not client:
            client = db.query(Client).filter(Client.id == user.id).first()
        if not client:
            client = db.query(Client).filter(Client.full_name == user.full_name).first()

        if not client:
            # Создаём клиента если его нет
            client = Client(
                full_name=user.full_name,
                passport_series="0000",
                passport_number="000000",
                phone="",
                email=user.email
            )
            db.add(client)
            db.commit()
            db.refresh(client)

        app_logger.info(f"✅ Вход клиента: {username} (ID={client.id})")
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="user_role", value="client", max_age=86400)
        response.set_cookie(key="user_id", value=str(client.id), max_age=86400)
        response.set_cookie(key="user_name", value=quote(user.full_name), max_age=86400)

        return response

    except Exception as e:
        app_logger.error(f"❌ Ошибка авторизации: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url=f"/login?error=❌ Ошибка авторизации: {str(e)}",
            status_code=303
        )


@app.post("/auth/register")
def process_register(
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: str = Form(None),
    passport_series: str = Form(...),
    passport_number: str = Form(...),
    passport_issue_date: str = Form(...),  # строка для парсинга
    passport_issue_place: str = Form(...),
    phone: str = Form(...),
    email: str = Form(None),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Регистрация нового клиента с паспортными данными."""
    try:
        # Проверка обязательных полей
        if not last_name.strip() or not first_name.strip() or not username.strip():
            return RedirectResponse(
                url="/login?error=❌ Обязательные поля не заполнены",
                status_code=303
            )

        # Проверка существования пользователя
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return RedirectResponse(
                url="/login?error=❌ Пользователь с таким логином уже существует",
                status_code=303
            )

        # Проверка email
        if email and email.strip():
            existing_email = db.query(User).filter(User.email == email.strip()).first()
            if existing_email:
                return RedirectResponse(
                    url="/login?error=❌ Email уже зарегистрирован",
                    status_code=303
                )

        # Проверка телефона
        existing_phone = db.query(Client).filter(Client.phone == phone).first()
        if existing_phone:
            return RedirectResponse(
                url="/login?error=❌ Телефон уже зарегистрирован",
                status_code=303
            )

        # Формируем полное имя
        full_name = f"{last_name} {first_name}"
        if middle_name and middle_name.strip():
            full_name += f" {middle_name.strip()}"

        # Парсим дату выдачи паспорта
        try:
            parsed_date = datetime.strptime(passport_issue_date, '%Y-%m-%d').date()
        except ValueError:
            return RedirectResponse(
                url="/login?error=❌ Неверный формат даты выдачи паспорта",
                status_code=303
            )

        # Создаём пользователя
        new_user = User(
            username=username,
            full_name=full_name,
            email=email.strip() if email and email.strip() else None,
            role=UserRole.USER,  # ✅ Правильная роль
            is_active=True
        )
        new_user.set_password(password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Создаём клиента с паспортными данными
        client = Client(
            full_name=full_name,
            passport_series=passport_series,
            passport_number=passport_number,
            phone=phone,
            email=email.strip() if email and email.strip() else None,
            passport_issue_date=parsed_date,  # ✅ Сохраняем дату
            passport_issue_place=passport_issue_place  # ✅ Сохраняем место
        )
        db.add(client)
        db.commit()
        db.refresh(client)

        # Авторизация
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="user_role", value="client", max_age=86400)
        response.set_cookie(key="user_id", value=str(client.id), max_age=86400)
        response.set_cookie(key="user_name", value=quote(full_name), max_age=86400)

        return response

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка регистрации: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url=f"/login?error=❌ Ошибка регистрации: {str(e)}",
            status_code=303
        )


@app.get("/auth/logout")
def process_logout():
    """Выход из системы."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("user_role")
    response.delete_cookie("user_id")
    response.delete_cookie("user_name")
    return response


@app.get("/profile", response_class=HTMLResponse)
def profile_page(
        request: Request,
        user_role: str = Cookie(default=None),
        user_id: str = Cookie(default=None),
        message: str = None,
        db: Session = Depends(get_db)
):
    """Страница профиля пользователя."""
    if not user_role or user_role != "client":
        raise HTTPException(status_code=403, detail="Доступ только для клиентов")

    client = db.query(Client).filter(Client.id == int(user_id)).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клиент не найден")

    return templates.TemplateResponse(
        request,
        "profile.html",
        {"client": client, "message": message}
    )


@app.post("/profile/update")
def update_profile(
        phone: str = Form(...),
        email: str = Form(None),
        address: str = Form(None),
        date_of_birth: date = Form(None),
        passport_issue_date: date = Form(None),
        passport_issue_place: str = Form(None),
        user_id: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Обновление профиля клиента."""
    client = db.query(Client).filter(Client.id == int(user_id)).first()
    if not client:
        raise HTTPException(status_code=404)

    client.phone = phone
    client.email = email
    if address:
        client.address = address
    if date_of_birth:
        client.date_of_birth = date_of_birth
    if passport_issue_date:
        client.passport_issue_date = passport_issue_date
    if passport_issue_place:
        client.passport_issue_place = passport_issue_place

    db.commit()
    return RedirectResponse(url="/profile?message=✅ Профиль обновлён", status_code=303)


@app.get("/car/{car_id}", response_class=HTMLResponse)
def car_detail(
        request: Request,
        car_id: int,
        user_role: str = Cookie(default=None),
        db: Session = Depends(get_db)
):
    """Детальная страница автомобиля."""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")

    car_status = get_car_status_text(car, db)

    car_with_image = {
        "id": car.id,
        "brand": car.brand,
        "model": car.model,
        "year": car.year,
        "transmission": car.transmission,
        "fuel_type": car.fuel_type,
        "color": car.color,
        "body_type": car.body_type,
        "seats": car.seats,
        "daily_rate": car.daily_rate,
        "description": car.description,
        "is_available": car.is_available,
        "image_url": get_car_image_url(car),
        "license_plate": car.license_plate,
        "engine_volume": car.engine_volume,
        "engine_power": car.engine_power,
        "status_text": car_status
    }

    return templates.TemplateResponse(
        request,
        "car_detail.html",
        {"car": car_with_image, "role": user_role}
    )


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(
        request: Request,
        user_role: str = Cookie(default=None),
        message: str = None,
        error: str = None,
        db: Session = Depends(get_db)
):
    """Админ-панель управления пользователями."""
    if user_role != "admin":
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    users = db.query(User).order_by(User.created_at.desc()).all()
    users_data = []
    for u in users:
        users_data.append({
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role.value,
            "is_active": u.is_active,
            "created_at": u.created_at.strftime("%d.%m.%Y %H:%M") if u.created_at else "—"
        })

    # Считаем количество ожидающих запросов
    pending_count = db.query(ReturnRequest).filter(
        ReturnRequest.status == ReturnRequestStatus.PENDING
    ).count()

    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            "users": users_data,
            "message": message,
            "error": error,
            "pending_count": pending_count
        }
    )


@app.get("/admin/user/{user_id}", response_class=HTMLResponse)
def admin_user_detail(
        request: Request,
        user_id: int,
        user_role: str = Cookie(default=None),
        message: str = None,
        error: str = None,
        db: Session = Depends(get_db)
):
    """Детальная информация о пользователе (админ) с реальной историей аренд."""
    if user_role not in ["admin", "superadmin", "manager"]:
        print(f"⚠️ Попытка доступа к профилю пользователя {user_id} с ролью {user_role}")
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/admin?error=❌ Пользователь не найден", status_code=303)

    # Ищем клиента по email (самый надёжный способ)
    client = None
    if user.email:
        client = db.query(Client).filter(Client.email == user.email).first()

    # Если не нашли по email, ищем по ID
    if not client:
        client = db.query(Client).filter(Client.id == user.id).first()

    # Если не нашли по ID, ищем по ФИО
    if not client:
        client = db.query(Client).filter(Client.full_name == user.full_name).first()

    # Если клиент не найден - создаём временный объект для отображения
    if not client:
        # Возвращаем страницу без данных клиента
        return templates.TemplateResponse(
            request,
            "admin_user_detail.html",
            {
                "user": user,
                "client": None,  # ✅ Передаём None вместо ошибки
                "client_rentals": [],
                "message": message,
                "error": "Клиент не найден в базе данных"
            }
        )

    # Если клиент не найден - создаём временный объект для отображения
    if not client:
        # Возвращаем страницу без данных клиента
        return templates.TemplateResponse(
            request,
            "admin_user_detail.html",
            {
                "user": user,
                "client": None,  # ✅ Передаём None вместо ошибки
                "client_rentals": [],
                "message": message,
                "error": "Клиент не найден в базе данных"
            }
        )

    # Получаем аренды клиента
    client_rentals = []
    if client:
        agreements = db.query(RentalAgreement).filter(
            RentalAgreement.client_id == client.id
        ).all()

        for a in agreements:
            car = db.query(Car).filter(Car.id == a.car_id).first()

            # Вычисляем длительность
            duration = 0
            if a.start_date and a.end_date:
                duration = (a.end_date - a.start_date).days

            client_rentals.append({
                "id": a.id,
                "car_info": f"{car.brand} {car.model} ({car.year})" if car else "Неизвестно",
                "start_date": a.start_date.strftime('%d.%m.%Y') if a.start_date else "—",
                "end_date": a.end_date.strftime('%d.%m.%Y') if a.end_date else "—",
                "duration": duration,
                "total_price": a.total_cost,
                "status": a.status.value if hasattr(a.status, 'value') else str(a.status)
            })

    return templates.TemplateResponse(
        request,
        "admin_user_detail.html",
        {
            "user": user,
            "client": client,
            "client_rentals": client_rentals,
            "message": message,
            "error": error
        }
    )


@app.post("/admin/user/{user_id}/update")
def admin_update_user(
        user_id: int,
        full_name: str = Form(...),
        email: str = Form(None),
        passport_series: str = Form(None),
        passport_number: str = Form(None),
        passport_issue_date: str = Form(None),
        passport_issue_place: str = Form(None),
        phone: str = Form(None),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Обновление данных пользователя администратором."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    old_name = user.full_name
    user.full_name = full_name
    user.email = email

    client = db.query(Client).filter(Client.full_name == old_name).first()
    if not client:
        client = db.query(Client).filter(Client.id == user_id).first()

    if client:
        client.full_name = full_name
        client.email = email
        if passport_series:
            client.passport_series = passport_series
        if passport_number:
            client.passport_number = passport_number
        if passport_issue_date:
            client.passport_issue_date = datetime.strptime(passport_issue_date, '%Y-%m-%d').date()
        if passport_issue_place:
            client.passport_issue_place = passport_issue_place
        if phone:
            client.phone = phone

    db.commit()

    return RedirectResponse(
        url=f"/admin/user/{user_id}?message=✅ Данные обновлены",
        status_code=303
    )


@app.post("/admin/user/{user_id}/toggle")
def toggle_user_status(
        user_id: int,
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Переключение статуса пользователя."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    if user.username == "super":
        return RedirectResponse(
            url="/admin?error=❌ Нельзя заблокировать главного администратора",
            status_code=303
        )

    user.is_active = not user.is_active
    db.commit()

    status_text = "разблокирован" if user.is_active else "заблокирован"
    return RedirectResponse(
        url=f"/admin?message=✅ Пользователь {status_text}",
        status_code=303
    )


@app.get("/admin/cars", response_class=HTMLResponse)
def admin_cars(
        request: Request,
        user_role: str = Cookie(default=None),
        message: str = None,
        error: str = None,
        db: Session = Depends(get_db)
):
    """Админ-панель управления автопарком."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    cars = db.query(Car).all()

    cars_with_images = []
    for car in cars:
        car_status = get_car_status_text(car, db)
        cars_with_images.append({
            "id": car.id,
            "brand": car.brand,
            "model": car.model,
            "year": car.year,
            "license_plate": car.license_plate,
            "transmission": car.transmission,
            "fuel_type": car.fuel_type,
            "color": car.color,
            "body_type": car.body_type,
            "seats": car.seats,
            "daily_rate": car.daily_rate,
            "description": car.description,
            "is_available": car.is_available,
            "image_url": get_car_image_url(car),
            "status_text": car_status
        })

    return templates.TemplateResponse(
        request,
        "admin_cars.html",
        {"cars": cars_with_images, "message": message, "error": error}
    )


@app.post("/admin/car/add")
def admin_add_car(
        brand: str = Form(...),
        model: str = Form(...),
        year: int = Form(...),
        daily_rate: float = Form(...),
        fuel_type: str = Form(...),
        transmission: str = Form(...),
        color: str = Form(...),
        seats: int = Form(...),
        body_type: str = Form(...),
        license_plate: str = Form(...),
        description: str = Form(None),
        image_url: str = Form(None),
        photo_file: UploadFile = File(None),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Добавление автомобиля администратором."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    existing = db.query(Car).filter(Car.license_plate == license_plate).first()
    if existing:
        return RedirectResponse(
            url="/admin/cars?error=❌ Автомобиль с таким номером уже существует",
            status_code=303
        )

    # Определяем путь к фото
    image_path = None

    if photo_file and photo_file.filename:
        # Загружаем файл
        if allowed_file(photo_file.filename):
            image_path = save_uploaded_file(photo_file, 0)  # 0 - временный ID
        else:
            return RedirectResponse(
                url="/admin/cars?error=❌ Недопустимый формат файла",
                status_code=303
            )
    elif image_url and image_url.strip():
        image_path = image_url.strip()
    else:
        image_path = "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=600&auto=format&fit=crop&q=80"

    new_car = Car(
        brand=brand,
        model=model,
        year=year,
        license_plate=license_plate,
        daily_rate=int(daily_rate),
        fuel_type=fuel_type,
        transmission=transmission,
        color=color,
        seats=seats,
        body_type=body_type,
        description=description,
        image_path=image_path,
        is_available=True
    )

    db.add(new_car)
    db.commit()

    return RedirectResponse(url="/admin/cars?message=✅ Автомобиль добавлен", status_code=303)

@app.post("/admin/car/{car_id}/update")
def admin_update_car(
        car_id: int,
        brand: str = Form(...),
        model: str = Form(...),
        year: int = Form(...),
        daily_rate: float = Form(...),
        fuel_type: str = Form(...),
        transmission: str = Form(...),
        color: str = Form(...),
        seats: int = Form(...),
        body_type: str = Form(...),
        license_plate: str = Form(...),
        description: str = Form(None),
        image_path: str = Form(None),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Обновление автомобиля администратором."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404)

    car.brand = brand
    car.model = model
    car.year = year
    car.license_plate = license_plate
    car.daily_rate = int(daily_rate)
    car.fuel_type = fuel_type
    car.transmission = transmission
    car.color = color
    car.seats = seats
    car.body_type = body_type
    car.description = description
    if image_path:
        car.image_path = image_path

    db.commit()

    return RedirectResponse(url="/admin/cars?message=✅ Автомобиль обновлён", status_code=303)


@app.post("/admin/car/{car_id}/upload-photo")
async def admin_upload_car_photo(
        car_id: int,
        file: UploadFile = File(...),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Загрузка фото автомобиля администратором."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404)

    if not file or not file.filename:
        return RedirectResponse(
            url="/admin/cars?error= Файл не выбран",
            status_code=303
        )

    if not allowed_file(file.filename):
        return RedirectResponse(
            url="/admin/cars?error=❌ Недопустимый формат. Разрешены: PNG, JPG, JPEG, WEBP",
            status_code=303
        )

    photo_path = save_uploaded_file(file, car_id)

    car.image_path = photo_path
    db.commit()

    return RedirectResponse(url="/admin/cars?message=✅ Фото загружено", status_code=303)


@app.post("/cars/{car_id}/status")
def change_car_status(
        car_id: int,
        new_status: str = Form(...),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Изменение статуса автомобиля."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404)

    if new_status == "available":
        car.is_available = True
    elif new_status == "maintenance":
        car.is_available = False

    db.commit()
    return RedirectResponse(url="/admin/cars?message=✅ Статус изменён", status_code=303)


@app.post("/rentals/create")
def create_rental(
        car_id: int = Form(...),
        start_date: date = Form(...),
        end_date: date = Form(...),
        user_id: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Создание новой аренды."""
    app_logger.info(f"📝 Создание аренды: car_id={car_id}, user_id={user_id}")
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car or not car.is_available:
        raise HTTPException(status_code=400, detail="Автомобиль недоступен")

    client = db.query(Client).filter(Client.id == int(user_id)).first()
    if not client:
        raise HTTPException(status_code=400, detail="Клиент не найден")

    days = (end_date - start_date).days
    if days <= 0:
        raise HTTPException(status_code=400, detail="Неверные даты")

    discount = 0.20 if days >= 14 else (0.10 if days >= 7 else 0.0)
    total_cost = int((days * car.daily_rate) * (1 - discount))

    agreement = RentalAgreement(
        client_id=client.id,
        car_id=car.id,
        start_date=start_date,
        end_date=end_date,
        total_cost=total_cost,
        status=AgreementStatus.ACTIVE
    )

    car.is_available = False
    db.add(agreement)
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/rentals/{rental_id}/return")
def return_car(
        rental_id: int,
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Завершение аренды и возврат автомобиля."""
    app_logger.info(f"🔄 Возврат автомобиля: rental_id={rental_id}, role={user_role}")
    if user_role != "admin":
        raise HTTPException(status_code=403)

    agreement = db.query(RentalAgreement).filter(RentalAgreement.id == rental_id).first()
    if not agreement or agreement.status != AgreementStatus.ACTIVE:
        return RedirectResponse(url="/", status_code=303)

    today = date.today()
    if today > agreement.end_date:
        overdue_days = (today - agreement.end_date).days
        car = db.query(Car).filter(Car.id == agreement.car_id).first()
        penalty_amount = overdue_days * (car.daily_rate * 2) if car else 0

        penalty = Penalty(
            agreement_id=agreement.id,
            penalty_type=PenaltyType.LATE_RETURN,
            amount=int(penalty_amount),
            description=f"Просрочка на {overdue_days} дней",
            status=PenaltyStatus.PENDING
        )
        db.add(penalty)
        agreement.total_cost += int(penalty_amount)

    agreement.status = AgreementStatus.COMPLETED
    car = db.query(Car).filter(Car.id == agreement.car_id).first()
    if car:
        car.is_available = True
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/rentals/{rental_id}/fine")
def create_fine(
        rental_id: int,
        penalty_type: str = Form(...),
        description: str = Form(...),
        amount: float = Form(...),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Выписка штрафа администратором."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    agreement = db.query(RentalAgreement).filter(RentalAgreement.id == rental_id).first()
    if not agreement:
        raise HTTPException(status_code=404)

    try:
        penalty_type_enum = PenaltyType(penalty_type)
    except ValueError:
        penalty_type_enum = PenaltyType.OTHER

    penalty = Penalty(
        agreement_id=agreement.id,
        penalty_type=penalty_type_enum,
        description=description.strip() if description else None,
        amount=int(amount),
        status=PenaltyStatus.PENDING
    )
    db.add(penalty)
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/fines/{fine_id}/pay")
def pay_fine(
        fine_id: int,
        db: Session = Depends(get_db)
):
    """Оплата штрафа."""
    penalty = db.query(Penalty).filter(Penalty.id == fine_id).first()
    if not penalty:
        raise HTTPException(status_code=404)

    penalty.is_paid = True
    penalty.status = PenaltyStatus.PAID
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.get("/rules", response_class=HTMLResponse)
def rules_page(request: Request):
    """Страница правил и договоров."""
    return templates.TemplateResponse(
        request,
        "rules.html"
    )


# ============================================================================
# ОТЧЁТЫ И СТАТИСТИКА (для админа)
# ============================================================================

@app.get("/admin/reports", response_class=HTMLResponse)
def admin_reports(
        request: Request,
        user_role: str = Cookie(default=None),
        db: Session = Depends(get_db)
):
    """Страница отчётов для админа."""
    if user_role not in ["admin", "superadmin", "manager"]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    # Базовая статистика
    total_cars = db.query(Car).count()
    available_cars = db.query(Car).filter(Car.is_available == True).count()
    total_clients = db.query(Client).count()
    total_agreements = db.query(RentalAgreement).count()
    active_agreements = db.query(RentalAgreement).filter(
        RentalAgreement.status == AgreementStatus.ACTIVE
    ).count()

    total_revenue = db.query(func.sum(RentalAgreement.total_cost)).scalar() or 0

    # Доход за текущий месяц
    current_month = date.today().replace(day=1)
    monthly_revenue = db.query(func.sum(RentalAgreement.total_cost)).filter(
        RentalAgreement.status == AgreementStatus.COMPLETED,
        RentalAgreement.end_date >= current_month
    ).scalar() or 0

    # Популярные автомобили
    popular_cars = db.query(
        Car.id, Car.brand, Car.model,
        func.count(RentalAgreement.id).label('rental_count')
    ).join(RentalAgreement).group_by(Car.id).order_by(
        func.count(RentalAgreement.id).desc()
    ).limit(5).all()

    # ✅ ИСПРАВЛЕНИЕ: Добавляем pending_count и другие недостающие переменные
    from models.return_request import ReturnRequest, ReturnRequestStatus
    from models.support_request import SupportRequest, SupportRequestStatus
    from models.penalty import Penalty

    pending_count = db.query(ReturnRequest).filter(
        ReturnRequest.status == ReturnRequestStatus.PENDING
    ).count()

    pending_support_count = db.query(SupportRequest).filter(
        SupportRequest.status == SupportRequestStatus.PENDING
    ).count()

    # Статистика штрафов
    total_penalties = db.query(Penalty).count()
    unpaid_penalties = db.query(Penalty).filter(Penalty.is_paid == False).count()
    paid_penalties_amount = db.query(func.sum(Penalty.amount)).filter(
        Penalty.is_paid == True
    ).scalar() or 0

    return templates.TemplateResponse(
        request, "admin_reports.html",
        {
            "total_cars": total_cars,
            "available_cars": available_cars,
            "total_clients": total_clients,
            "total_agreements": total_agreements,
            "active_agreements": active_agreements,
            "total_revenue": int(total_revenue),
            "monthly_revenue": int(monthly_revenue),
            "popular_cars": popular_cars,
            "pending_count": pending_count,
            "pending_support_count": pending_support_count,
            "total_penalties": total_penalties,
            "unpaid_penalties": unpaid_penalties,
            "paid_penalties_amount": int(paid_penalties_amount),
            "role": user_role
        }
    )

# ============================================================================
# ТЕХНИЧЕСКОЕ ОБСЛУЖИВАНИЕ
# ============================================================================

@app.get("/admin/maintenance", response_class=HTMLResponse)
def admin_maintenance(
        request: Request,
        user_role: str = Cookie(default=None),
        message: str = None,
        error: str = None,
        db: Session = Depends(get_db)
):
    """Страница управления ТО."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    # Получаем автомобили на ТО (недоступные и без активной аренды)
    cars_on_maintenance = db.query(Car).filter(Car.is_available == False).all()

    return templates.TemplateResponse(
        request,
        "admin_maintenance.html",
        {
            "cars": cars_on_maintenance,
            "message": message,
            "error": error
        }
    )


@app.post("/admin/car/{car_id}/maintenance")
def add_car_maintenance(
        car_id: int,
        description: str = Form(...),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Постановка автомобиля на ТО."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404)

    car.is_available = False
    db.commit()

    return RedirectResponse(
        url="/admin/maintenance?message=✅ Автомобиль поставлен на ТО",
        status_code=303
    )

@app.post("/admin/car/{car_id}/return-from-maintenance")
def return_car_from_maintenance(
        car_id: int,
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Возврат автомобиля с ТО."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404)

    car.is_available = True
    db.commit()

    return RedirectResponse(
        url="/admin/maintenance?message=✅ Автомобиль возвращён в строй",
        status_code=303
    )

# ============================================================================
# ПЛАТЕЖИ
# ============================================================================

@app.get("/payments", response_class=HTMLResponse)
def payments_page(
        request: Request,
        user_role: str = Cookie(default=None),
        user_id: str = Cookie(default=None),
        db: Session = Depends(get_db)
):
    """Страница платежей."""
    if not user_role:
        raise HTTPException(status_code=403)

    if user_role == "client":
        # Показываем платежи клиента
        client = db.query(Client).filter(Client.id == int(user_id)).first()
        if not client:
            raise HTTPException(status_code=404)

        agreements_db = db.query(RentalAgreement).filter(RentalAgreement.client_id == client.id).all()
    else:
        # Админ видит все платежи
        agreements_db = db.query(RentalAgreement).all()

    # Формируем данные для UI
    agreements_ui = []
    for a in agreements_db:
        client = db.query(Client).filter(Client.id == a.client_id).first()
        car = db.query(Car).filter(Car.id == a.car_id).first()

        agreements_ui.append({
            "id": a.id,
            "client_name": client.full_name if client else "Неизвестно",
            "car_info": f"{car.brand} {car.model}" if car else "Неизвестно",
            "period": f"{a.start_date.strftime('%d.%m.%Y')} — {a.end_date.strftime('%d.%m.%Y')}" if a.start_date and a.end_date else "—",
            "total_price": a.total_cost,
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status)
        })

    return templates.TemplateResponse(
        request,
        "payments.html",
        {
            "agreements": agreements_ui,
            "role": user_role
        }
    )

# ============================================================================
# ЗАПРОСЫ НА ВОЗВРАТ (УВЕДОМЛЕНИЯ В СУ)
# ============================================================================

@app.post("/rentals/{rental_id}/request-return")
def request_return(
        rental_id: int,
        user_role: str = Cookie(...),
        user_id: str = Cookie(...),
        db: Session = Depends(get_db)
):
    logger.info(f"Получен запрос на возврат аренды #{rental_id}")
    logger.info(f"User role: {user_role}, User ID: {user_id}")
    """Создание запроса на возврат автомобиля (уведомление в СУ)."""
    try:
        from return_request import ReturnRequest, ReturnRequestStatus
    except ImportError:
        return RedirectResponse(
            url="/?message=❌ Функция временно недоступна",
            status_code=303
        )

    # Получаем аренду
    agreement = db.query(RentalAgreement).filter(RentalAgreement.id == rental_id).first()
    if not agreement:
        raise HTTPException(status_code=404, detail="Аренда не найдена")

    # Проверяем что это аренда текущего клиента
    if user_role == "client" and agreement.client_id != int(user_id):
        raise HTTPException(status_code=403, detail="Это не ваша аренда")

    # Проверяем статус аренды
    if agreement.status != AgreementStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Аренда не активна")

    # Проверяем есть ли уже pending запрос
    existing_request = db.query(ReturnRequest).filter(
        ReturnRequest.rental_id == rental_id,
        ReturnRequest.status == ReturnRequestStatus.PENDING
    ).first()

    if existing_request:
        return RedirectResponse(
            url="/?message=⏳ Запрос на возврат уже отправлен и ожидает подтверждения",
            status_code=303
        )

    # Получаем данные клиента и авто
    client = db.query(Client).filter(Client.id == agreement.client_id).first()
    car = db.query(Car).filter(Car.id == agreement.car_id).first()

    # Создаём запрос на возврат
    return_request = ReturnRequest(
        rental_id=agreement.id,
        client_id=agreement.client_id,
        car_id=agreement.car_id,
        client_name=client.full_name if client else "Неизвестно",
        car_info=f"{car.brand} {car.model} ({car.license_plate})" if car else "Неизвестно",
        rental_period=f"{agreement.start_date.strftime('%d.%m.%Y')} — {agreement.end_date.strftime('%d.%m.%Y')}",
        status=ReturnRequestStatus.PENDING
    )

    db.add(return_request)
    db.commit()

    # СОЗДАЕМ УВЕДОМЛЕНИЕ
    try:
        notification_service = NotificationService(db)  # <-- Передаем db
        notification_service.notify_return_request(return_request)
    except Exception as e:
        logger.error(f"Ошибка создания уведомления: {e}")

    logger.info(f"Создан запрос на возврат: {return_request.id}")
    logger.info(f"Данные: client={return_request.client_name}, car={return_request.car_info}")

    return RedirectResponse(
        url="/?message=✅ Запрос на возврат отправлен. Ожидайте подтверждения администратора.",
        status_code=303
    )


@app.get("/admin/return-requests", response_class=HTMLResponse)
def admin_return_requests(
        request: Request,
        user_role: str = Cookie(default=None),
        message: str = None,
        error: str = None,
        db: Session = Depends(get_db)
):
    """Страница управления запросами на возврат (для админа)."""
    try:
        from return_request import ReturnRequest, ReturnRequestStatus
    except ImportError:
        raise HTTPException(status_code=500, detail="Модель ReturnRequest не найдена")

    if user_role != "admin":
        raise HTTPException(status_code=403)

    # Получаем все запросы на возврат
    return_requests = db.query(ReturnRequest).order_by(
        ReturnRequest.request_date.desc()
    ).all()

    requests_data = []
    for req in return_requests:
        requests_data.append({
            "id": req.id,
            "rental_id": req.rental_id,
            "client_name": req.client_name,
            "car_info": req.car_info,
            "rental_period": req.rental_period,
            "request_date": req.request_date.strftime("%d.%m.%Y %H:%M"),
            "status": req.status.value,
            "admin_comment": req.admin_comment or ""
        })

    return templates.TemplateResponse(
        request,
        "admin_return_requests.html",
        {
            "return_requests": requests_data,
            "message": message,
            "error": error
        }
    )


@app.post("/admin/return-requests/{request_id}/approve")
def approve_return_request(
        request_id: int,
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Подтверждение запроса на возврат (админ)."""
    try:
        from return_request import ReturnRequest, ReturnRequestStatus
    except ImportError:
        raise HTTPException(status_code=500, detail="Модель ReturnRequest не найдена")

    if user_role != "admin":
        raise HTTPException(status_code=403)

    return_req = db.query(ReturnRequest).filter(ReturnRequest.id == request_id).first()
    if not return_req:
        raise HTTPException(status_code=404)

    if return_req.status != ReturnRequestStatus.PENDING:
        return RedirectResponse(
            url="/admin/return-requests?error=❌ Запрос уже обработан",
            status_code=303
        )

    return_req.status = ReturnRequestStatus.APPROVED
    return_req.admin_decision_date = datetime.utcnow()

    # Завершаем аренду
    agreement = db.query(RentalAgreement).filter(RentalAgreement.id == return_req.rental_id).first()
    if agreement and agreement.status == AgreementStatus.ACTIVE:
        agreement.status = AgreementStatus.COMPLETED

        # Возвращаем авто в доступные
        car = db.query(Car).filter(Car.id == return_req.car_id).first()
        if car:
            car.is_available = True

    db.commit()

    return RedirectResponse(
        url="/admin/return-requests?message=✅ Возврат подтвержден. Аренда завершена.",
        status_code=303
    )


@app.post("/admin/return-requests/{request_id}/reject")
def reject_return_request(
        request_id: int,
        comment: str = Form(...),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Отклонение запроса на возврат (админ)."""
    try:
        from return_request import ReturnRequest, ReturnRequestStatus
    except ImportError:
        raise HTTPException(status_code=500, detail="Модель ReturnRequest не найдена")

    if user_role != "admin":
        raise HTTPException(status_code=403)

    return_req = db.query(ReturnRequest).filter(ReturnRequest.id == request_id).first()
    if not return_req:
        raise HTTPException(status_code=404)

    if return_req.status != ReturnRequestStatus.PENDING:
        return RedirectResponse(
            url="/admin/return-requests?error=❌ Запрос уже обработан",
            status_code=303
        )

    return_req.status = ReturnRequestStatus.REJECTED
    return_req.admin_decision_date = datetime.utcnow()
    return_req.admin_comment = comment

    db.commit()

    return RedirectResponse(
        url="/admin/return-requests?message=❌ Запрос отклонен.",
        status_code=303
    )


# ============================================================================
# ОБРАЩЕНИЯ В ПОДДЕРЖКУ
# ============================================================================

from models.support_request import SupportRequest, SupportRequestStatus


@app.post("/support/request")
def support_request(
        subject: str = Form(...),
        description: str = Form(...),
        user_role: str = Cookie(...),
        user_id: str = Cookie(...),
        user_name: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Создание обращения в службу поддержки."""
    app_logger.info(f"📩 Новое обращение: subject={subject}, user_id={user_id}")
    try:
        from support_request import SupportRequest, SupportRequestStatus
        from utils.notification_service import NotificationService
    except ImportError:
        return RedirectResponse(
            url="/profile?message=❌ Ошибка: таблица обращений не найдена",
            status_code=303
        )

    display_name = unquote(user_name) if user_name else "Неизвестно"

    request = SupportRequest(
        client_id=int(user_id),
        client_name=display_name,
        subject=subject,
        description=description,
        status=SupportRequestStatus.PENDING
    )

    db.add(request)
    db.commit()

    # СОЗДАЕМ УВЕДОМЛЕНИЕ ДЛЯ АДМИНОВ
    try:
        notification_service = NotificationService(db)
        notification_service.notify_support_request(request)
    except Exception as e:
        print(f"Ошибка создания уведомления: {e}")

    return RedirectResponse(
        url="/profile?message=✅ Обращение отправлено. Мы ответим в ближайшее время.",
        status_code=303
    )


@app.get("/admin/support-requests", response_class=HTMLResponse)
def admin_support_requests(
    request: Request,
    user_role: str = Cookie(default=None),
    message: str = None,
    db: Session = Depends(get_db)
):
    """Просмотр обращений в поддержку (админ)."""
    from utils.dev_console import dev_logger, log_support_request_action, log_template_render

    log_support_request_action("ЗАПРОС СПИСКА ОБРАЩЕНИЙ", details=f"user_role={user_role}")

    if user_role not in ["admin", "superadmin", "manager"]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    try:
        from support_request import SupportRequest, SupportRequestStatus
        requests = db.query(SupportRequest).order_by(SupportRequest.created_at.desc()).all()

        # ✅ ЛОГИРОВАНИЕ: Проверяем статусы всех обращений
        for req in requests:
            status_value = req.status.value if hasattr(req.status, 'value') else str(req.status)
            status_type = type(req.status).__name__
            dev_logger.info(
                f"[ОБРАЩЕНИЕ #{req.id}] "
                f"status.value='{status_value}', "
                f"type={status_type}, "
                f"client={req.client_name}, "
                f"subject={req.subject}"
            )

        # Преобразуем статусы для шаблона
        requests_data = []
        for req in requests:
            status_value = req.status.value if hasattr(req.status, 'value') else str(req.status)
            requests_data.append({
                "id": req.id,
                "client_name": req.client_name,
                "subject": req.subject,
                "description": req.description,
                "status": status_value,
                "created_at": req.created_at,
                "updated_at": req.updated_at,
                "admin_response": req.admin_response
            })

            # Логируем для отладки
            print(f"✅ Обращение #{req.id}: status='{status_value}'")

            dev_logger.info(
                f"[ДАННЫЕ ДЛЯ ШАБЛОНА] ID={req.id}, status='{status_value}'"
            )

        log_template_render("admin_support_requests.html", ["requests", "message"])

        return templates.TemplateResponse(
            request,
            "admin_support_requests.html",
            {
                "requests": requests_data,
                "message": message
            }
        )
    except ImportError as e:
        log_error("ImportError в admin_support_requests", e)
        raise HTTPException(status_code=500, detail="Таблица обращений не найдена")
    except Exception as e:
        log_error("Ошибка в admin_support_requests", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/user/{user_id}/change-credentials")
def admin_change_user_credentials(
        user_id: int,
        new_username: str = Form(...),
        new_password: str = Form(None),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Изменение логина и пароля пользователя админом."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)

    if user.username == "super":
        return RedirectResponse(
            url="/admin/user/{user_id}?error=❌ Нельзя изменить данные главного администратора",
            status_code=303
        )

    # Проверка уникальности логина
    if new_username != user.username:
        existing = db.query(User).filter(User.username == new_username).first()
        if existing:
            return RedirectResponse(
                url=f"/admin/user/{user_id}?error=❌ Пользователь с таким логином уже существует",
                status_code=303
            )

    old_username = user.username
    user.username = new_username

    # Если указан новый пароль
    if new_password and new_password.strip():
        user.set_password(new_password)

    db.commit()

    return RedirectResponse(
        url=f"/admin/user/{user_id}?message=✅ Логин и пароль изменены",
        status_code=303
    )

@app.get("/rules", response_class=HTMLResponse)
def rules_page(request: Request):
    """Страница правил и договоров."""
    return templates.TemplateResponse(request, "rules.html")


@app.post("/admin/support-requests/{request_id}/reply")
def admin_reply_support_request(
    request_id: int,  # ✅ Path parameter (из URL)
    response: str = Form(...),  # ✅ Form parameter (из формы)
    user_role: str = Cookie(...),
    db: Session = Depends(get_db)
):
    """Ответ админа на обращение в поддержку."""
    from utils.dev_console import dev_logger, log_support_request_action, log_status_change

    log_support_request_action("ОТВЕТ АДМИНА", request_id, f"user_role={user_role}")

    if user_role not in ["admin", "superadmin", "manager"]:
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    try:
        from support_request import SupportRequest, SupportRequestStatus
        from models.notification import Notification

        support_req = db.query(SupportRequest).filter(
            SupportRequest.id == request_id
        ).first()

        if not support_req:
            raise HTTPException(status_code=404)

        # ✅ ЛОГИРОВАНИЕ: Старый статус
        old_status = support_req.status.value if hasattr(support_req.status, 'value') else str(support_req.status)
        dev_logger.info(f"[ОБРАЩЕНИЕ #{request_id}] Старый статус: '{old_status}'")

        support_req.status = SupportRequestStatus.IN_PROGRESS
        support_req.admin_response = response
        support_req.updated_at = datetime.utcnow()

        # ✅ ЛОГИРОВАНИЕ: Новый статус
        new_status = support_req.status.value if hasattr(support_req.status, 'value') else str(support_req.status)
        log_status_change("Обращение", request_id, old_status, new_status)

        # Создаем уведомление
        notification = Notification(
            title="📨 Ответ от поддержки",
            message=f"По вашему обращению '#{request_id}': {response}",
            notification_type="support_response",
            priority="medium",
            user_id=support_req.client_id,
            is_read=False
        )
        db.add(notification)
        db.commit()

        dev_logger.info(f"[ОБРАЩЕНИЕ #{request_id}] Ответ сохранен, уведомление создано")

        return RedirectResponse(
            url="/admin/support-requests?message=✅ Ответ отправлен пользователю",
            status_code=303
        )
    except Exception as e:
        log_error("Ошибка в admin_reply_support_request", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/support-requests", response_class=HTMLResponse)
def user_support_requests_page(
        request: Request,
        user_role: str = Cookie(default=None),
        user_id: str = Cookie(default=None),
        db: Session = Depends(get_db)
):
    """Страница просмотра обращений пользователя."""
    if user_role != "client":
        raise HTTPException(status_code=403, detail="Доступ только для клиентов")

    try:
        from support_request import SupportRequest
        requests = db.query(SupportRequest).filter(
            SupportRequest.client_id == int(user_id)
        ).order_by(SupportRequest.created_at.desc()).all()

        return templates.TemplateResponse(
            request,
            "user_support_requests.html",
            {"requests": requests}
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Таблица обращений не найдена")


@app.get("/user/support-requests/{request_id}", response_class=HTMLResponse)
def user_support_request_detail(
    request: Request,  # ← СТАНДАРТНОЕ имя для FastAPI
    request_id: int,
    user_role: str = Cookie(default=None),
    user_id: str = Cookie(default=None),
    db: Session = Depends(get_db)
):
    """Детальный просмотр обращения пользователем."""
    if user_role != "client":
        raise HTTPException(status_code=403, detail="Доступ только для клиентов")
    try:
        from support_request import SupportRequest
        support_req = db.query(SupportRequest).filter(
            SupportRequest.id == request_id,
            SupportRequest.client_id == int(user_id)
        ).first()

        if not support_req:
            raise HTTPException(status_code=404, detail="Обращение не найдено")

        return templates.TemplateResponse(
            request,
            "support_request_detail.html",
            {"support_request": support_req}  # ← передаём как support_request
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Таблица обращений не найдена")

@app.post("/user/support-requests/{request_id}/message")
def user_send_support_message(
        request_id: int,
        message: str = Form(...),
        user_role: str = Cookie(...),
        user_id: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Отправка сообщения клиентом в обращении."""
    if user_role != "client":
        raise HTTPException(status_code=403)

    try:
        from support_request import SupportRequest
        from support_message import SupportMessage
        from models.notification import Notification

        support_req = db.query(SupportRequest).filter(
            SupportRequest.id == request_id,
            SupportRequest.client_id == int(user_id)
        ).first()

        if not support_req:
            raise HTTPException(status_code=404)

        # Сохраняем сообщение
        new_message = SupportMessage(
            support_request_id=request_id,
            sender_type="client",
            sender_id=int(user_id),
            message=message
        )
        db.add(new_message)

        support_req.status = SupportRequestStatus.IN_PROGRESS  # ✅ Правильно
        support_req.updated_at = datetime.utcnow()

        # Создаем уведомление для админов
        notification = Notification(
            title=f"📨 Новое сообщение в обращении #{request_id}",
            message=f"Клиент отправил сообщение: {message[:100]}...",
            notification_type="support_message",
            priority="medium",
            agreement_id=request_id,  # ✅ ID обращения для открытия деталей
            user_id=None,  # Все админы
            is_read=False
        )
        db.add(notification)

        # Также создаём SupportMessage для отображения в обращении
        try:
            from models.support_message import SupportMessage
            support_msg = SupportMessage(
                support_request_id=request_id,
                sender_type="client",
                sender_id=int(user_id),
                message=message
            )
            db.add(support_msg)

        except Exception as e:
            print(f"⚠️ Ошибка создания SupportMessage: {e}")

        db.commit()

        return RedirectResponse(
            url=f"/user/support-requests/{request_id}?message=✅ Сообщение отправлено",
            status_code=303
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Таблица не найдена")


@app.post("/user/support-requests/{request_id}/reopen")
def user_reopen_support_request(
        request_id: int,
        additional_info: str = Form(...),
        attachment: UploadFile = File(None),
        user_role: str = Cookie(...),
        user_id: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Продолжение обращения пользователем с загрузкой файлов."""
    if user_role != "client":
        raise HTTPException(status_code=403)

    try:
        from support_request import SupportRequest, SupportRequestStatus
        from models.notification import Notification

        support_req = db.query(SupportRequest).filter(
            SupportRequest.id == request_id,
            SupportRequest.client_id == int(user_id)
        ).first()

        if not support_req:
            raise HTTPException(status_code=404)

        support_req.status = SupportRequestStatus.IN_PROGRESS
        support_req.updated_at = datetime.utcnow()
        print(f"✅ Обращение #{request_id} продолжено пользователем. Статус изменен на IN_PROGRESS")

        # Добавляем дополнительную информацию
        if additional_info:
            support_req.description += f"\n\n[Дополнительно от клиента {datetime.now().strftime('%d.%m.%Y %H:%M')}]:\n{additional_info}"

        # Обработка файла (если загружен)
        if attachment and attachment.filename:
            # Проверяем размер файла (максимум 5 МБ)
            content = attachment.file.read()
            if len(content) > 5 * 1024 * 1024:
                return RedirectResponse(
                    url=f"/user/support-requests/{request_id}?message=❌ Файл слишком большой (максимум 5 МБ)",
                    status_code=303
                )
            attachment.file.seek(0)

            # Сохраняем файл
            from pathlib import Path
            upload_dir = Path("static/support_attachments")
            upload_dir.mkdir(parents=True, exist_ok=True)

            filename = f"{request_id}_{uuid.uuid4().hex}_{attachment.filename}"
            filepath = upload_dir / filename

            with open(filepath, "wb") as buffer:
                buffer.write(content)

            support_req.description += f"\n\n[Прикреплен файл]: /static/support_attachments/{filename}"

        # Создаем уведомление для админов
        notification = Notification(
            title=f"🔄 Обращение #{request_id} продолжено",
            message=f"Клиент дополнил обращение:\n{additional_info[:100]}...",
            notification_type="support_message",
            priority="medium",
            agreement_id=request_id,  # ✅ ID обращения для открытия деталей
            user_id=None,  # Все админы
            is_read=False
        )
        db.add(notification)

        db.commit()

        print(f"✅ Уведомление создано для админов о продолжении обращения #{request_id}")

        return RedirectResponse(
            url=f"/user/support-requests/{request_id}?message=✅ Обращение продолжено",
            status_code=303
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Таблица обращений не найдена")


@app.post("/user/support-requests/{request_id}/reopen")
async def user_support_request_reopen(
        request_id: int,
        additional_info: str = Form(...),
        attachments: List[UploadFile] = File(default=[]),
        db: Session = Depends(get_db)
):
    # 1. Ищем существующее обращение
    # Примечание: Замените SupportRequest на фактическое имя вашей модели из web_models
    support_req = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
    if not support_req:
        raise HTTPException(status_code=404, detail="Обращение не найдено")

    # 2. Переводим статус обратно в активный (например, PENDING или OPEN в зависимости от вашего Enum)
    try:
        support_req.status = SupportRequestStatus.PENDING
    except NameError:
        support_req.status = "pending"  # если используется обычная строка

    support_req.updated_at = datetime.utcnow()

    # 3. Обработка прикрепленных файлов (если они загружены)
    saved_file_paths = []
    for file in attachments:
        if file.filename:  # Проверяем, что файл действительно выбран
            # Генерация уникального имени для предотвращения перезаписи
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = IMAGES_DIR / unique_filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            saved_file_paths.append(f"/images/{unique_filename}")

    # 4. Сохраняем сообщение пользователя в историю переписки обращения
    # Примечание: Замените SupportMessage на имя вашей модели сообщений (из списка таблиц: support_messages)
    try:
        new_message = SupportMessage(
            request_id=support_req.id,
            sender_role="client",
            message_text=additional_info,
            attachments=",".join(saved_file_paths) if saved_file_paths else None,
            created_at=datetime.utcnow()
        )
        db.add(new_message)
    except Exception as e:
        logger.error(f"Не удалось сохранить сообщение в support_messages: {e}")

    # 5. Логируем аудит-событие (судя по структуре таблиц audit_logs)
    logger.info(f"Пользователь возобновил обращение #{request_id}. Прикреплено файлов: {len(saved_file_paths)}")

    db.commit()

    # Перенаправляем обратно на страницу детализации с уведомлением об успешном открытии
    return RedirectResponse(
        url=f"/user/support-requests/{request_id}?message=🔄 Обращение возобновлено и передано администратору",
        status_code=303
    )

@app.post("/admin/support-requests/{request_id}/message")
def admin_send_support_message(
        request_id: int,
        message: str = Form(...),
        user_role: str = Cookie(...),
        user_id: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Отправка сообщения админом в обращении."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    try:
        from support_request import SupportRequest
        from support_message import SupportMessage
        from models.notification import Notification

        support_req = db.query(SupportRequest).filter(
            SupportRequest.id == request_id
        ).first()

        if not support_req:
            raise HTTPException(status_code=404)

        # Сохраняем сообщение
        new_message = SupportMessage(
            support_request_id=request_id,
            sender_type="admin",
            sender_id=int(user_id),
            message=message
        )
        db.add(new_message)

        support_req.updated_at = datetime.utcnow()

        # Создаем уведомление для клиента
        notification = Notification(
            title=f"📨 Ответ от поддержки по обращению #{request_id}",
            message=message[:200],
            notification_type="support_response",
            priority="medium",
            user_id=support_req.client_id,
            is_read=False
        )
        db.add(notification)

        db.commit()

        return RedirectResponse(
            url=f"/admin/support-requests/{request_id}?message=✅ Сообщение отправлено",
            status_code=303
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Таблица не найдена")

@app.post("/notifications/{notification_id}/read")
def mark_notification_read(
        notification_id: int,
        user_role: str = Cookie(...),
        user_id: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Отметить уведомление как прочитанное."""
    try:
        from models.notification import Notification, NotificationRead
        from datetime import datetime

        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()

        if not notification:
            raise HTTPException(status_code=404)

        # Проверяем что уведомление принадлежит пользователю
        if user_role == "client" and notification.user_id != int(user_id):
            raise HTTPException(status_code=403)

        # Проверяем, не отмечал ли уже этот пользователь это уведомление
        existing_read = db.query(NotificationRead).filter(
            NotificationRead.notification_id == notification_id,
            NotificationRead.user_id == int(user_id)
        ).first()

        if not existing_read:
            # Создаём запись о прочтении для конкретного пользователя
            new_read = NotificationRead(
                notification_id=notification_id,
                user_id=int(user_id)
            )
            db.add(new_read)

            # Если уведомление личное (user_id совпадает), также ставим is_read=True
            if notification.user_id == int(user_id):
                notification.is_read = True

            db.commit()

        # Возвращаем новый счетчик непрочитанных
        if user_role == "admin":
            # Для админов: общие уведомления (user_id=None) + личные
            read_ids = [r.notification_id for r in db.query(NotificationRead).filter(
                NotificationRead.user_id == int(user_id)
            ).all()]

            unread_count = db.query(Notification).filter(
                Notification.is_read == False,
                (Notification.user_id == None) | (Notification.user_id == int(user_id)),
                ~Notification.id.in_(read_ids) if read_ids else True
            ).count()
        else:
            unread_count = db.query(Notification).filter(
                Notification.user_id == int(user_id),
                Notification.is_read == False
            ).count()

        return {"success": True, "unread_count": unread_count}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

@app.post("/admin/support-requests/{request_id}/reply")
def admin_reply_to_support_request(
        request_id: int,
        response: str = Form(...),
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Ответ админа на обращение с созданием уведомления."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    try:
        from models.support_request import SupportRequest, SupportRequestStatus
        from models.support_message import SupportMessage
        from models.notification import Notification
        from datetime import datetime

        support_req = db.query(SupportRequest).filter(
            SupportRequest.id == request_id
        ).first()

        if not support_req:
            raise HTTPException(status_code=404, detail="Обращение не найдено")

        # 1. Сохраняем ответ
        support_req.admin_response = response
        support_req.status = SupportRequestStatus.IN_PROGRESS
        support_req.updated_at = datetime.utcnow()

        # 2. Создаём SupportMessage
        support_msg = SupportMessage(
            support_request_id=request_id,
            sender_type="admin",
            sender_id=0,  # ID админа если есть
            message=response
        )
        db.add(support_msg)

        # 3. Добавляем в description
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        support_req.description += f"\n\n[Ответ поддержки {timestamp}]:\n{response}"

        # 4. Создаём уведомление для пользователя
        notification = Notification(
            title="📨 Ответ от поддержки",
            message=f"По вашему обращению #{request_id}:\n{response[:200]}",
            notification_type="support_message",
            priority="medium",
            user_id=support_req.client_id,
            agreement_id=request_id,
            is_read=False
        )
        db.add(notification)

        db.commit()

        return RedirectResponse(
            url=f"/admin/support-requests/{request_id}?message=✅ Ответ отправлен",
            status_code=303
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@app.post("/admin/support-requests/{request_id}/resolve")
def admin_resolve_support_request(
        request_id: int,
        user_role: str = Cookie(...),
        db: Session = Depends(get_db)
):
    """Закрытие обращения как решенного."""
    if user_role != "admin":
        raise HTTPException(status_code=403)

    try:
        from support_request import SupportRequest, SupportRequestStatus
        from models.notification import Notification

        support_req = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
        if not support_req:
            raise HTTPException(status_code=404)

        support_req.status = SupportRequestStatus.RESOLVED
        support_req.resolved_at = datetime.utcnow()
        support_req.updated_at = datetime.utcnow()

        # Создаем уведомление для клиента
        notification = Notification(
            title=f"✅ Обращение #{request_id} решено",
            message=f"Ваше обращение '{support_req.subject}' было успешно решено. Спасибо за обращение!",
            notification_type="support_resolved",
            priority="medium",
            user_id=support_req.client_id,
            is_read=False
        )
        db.add(notification)

        db.commit()

        return RedirectResponse(
            url="/admin/support-requests?message=✅ Обращение закрыто как решенное",
            status_code=303
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="Таблица обращений не найдена")


@app.get("/admin/support-requests/{request_id}", response_class=HTMLResponse)
def admin_support_request_detail(
        request: Request,
        request_id: int,
        user_role: str = Cookie(default=None),
        db: Session = Depends(get_db)
):
    """Детальный просмотр обращения админом."""
    from utils.dev_console import dev_logger, log_support_request_action, log_template_render

    log_support_request_action("ЗАПРОС ДЕТАЛЕЙ ОБРАЩЕНИЯ", request_id, f"user_role={user_role}")

    if user_role != "admin":
        raise HTTPException(status_code=403)

    try:
        from support_request import SupportRequest
        support_req = db.query(SupportRequest).filter(
            SupportRequest.id == request_id
        ).first()

        if not support_req:
            dev_logger.warning(f"[ОБРАЩЕНИЕ #{request_id}] Не найдено в БД")
            raise HTTPException(status_code=404)

        # ✅ ЛОГИРОВАНИЕ: Проверяем статус
        status_value = support_req.status.value if hasattr(support_req.status, 'value') else str(support_req.status)
        status_type = type(support_req.status).__name__

        dev_logger.info(
            f"[ОБРАЩЕНИЕ #{request_id}] "
            f"status.value='{status_value}', "
            f"type={status_type}, "
            f"client={support_req.client_name}"
        )

        log_template_render("admin_support_request_detail.html", ["support_request"])

        return templates.TemplateResponse(
            request,
            "admin_support_request_detail.html",
            {"support_request": support_req}
        )
    except ImportError as e:
        log_error("ImportError в admin_support_request_detail", e)
        raise HTTPException(status_code=500, detail="Таблица обращений не найдена")
    except Exception as e:
        log_error("Ошибка в admin_support_request_detail", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/dev-logs", response_class=HTMLResponse)
def dev_logs_page(
        request: Request,
        user_role: str = Cookie(default=None)
):
    """Страница просмотра логов (только для админов)."""
    if user_role not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Доступ только для администраторов")

    logs = []
    # Ищем лог-файл веб-портала
    log_file = PROJECT_ROOT / "logs" / "web_portal.log"

    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            # Читаем последние 200 строк
            for line in f.readlines()[-200:]:
                line = line.strip()
                if not line:
                    continue

                # Парсим формат: INFO:     127.0.0.1:58080 - "GET / HTTP/1.1" 200 OK
                if ' - ' in line:
                    parts = line.split(' - ', 2)
                    if len(parts) >= 3:
                        time_str = parts[0].strip()
                        level = parts[1].strip()
                        message = parts[2].strip()

                        logs.append({
                            "time": time_str,
                            "level": level,
                            "message": message
                        })
                else:
                    # Для строк без разделителя
                    logs.append({
                        "time": "",
                        "level": "INFO",
                        "message": line
                    })
    else:
        logs.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "WARNING",
            "message": f"Файл логов не найден: {log_file.absolute()}"
        })

    return templates.TemplateResponse(
        request,
        "dev_logs.html",
        {"logs": logs}
    )

if __name__ == "__main__":
    print("🚀 Запуск ДрайвКонтроль...")
    print("🌐 Откройте: http://127.0.0.1:8000")
    print("🔐 Админ-панель: http://127.0.0.1:8000/admin")
    print(" Управление автопарком: http://127.0.0.1:8000/admin/cars")
    print("📋 Правила и договоры: http://127.0.0.1:8000/rules")
    print("Техническое обслуживание","http://127.0.0.1:8000/admin/maintenance")
    print("Отчеты и статистика для админов","http://127.0.0.1:8000/admin/reports")
    print("Скрытая ссылка с логами для разработчика:", "http://127.0.0.1:8000/dev-logs")
    print("Документация OpenAPI:", "http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
