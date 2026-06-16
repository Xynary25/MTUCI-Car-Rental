"""
Модуль планирования автоматического резервного копирования.
Использует APScheduler для выполнения бэкапов по расписанию.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from utils.system_utils import create_database_backup, cleanup_old_backups
from database import SessionLocal
from utils.logger import app_logger
import os
import atexit
import threading


class BackupScheduler:
    """Планировщик автоматического резервного копирования."""

    def __init__(self):
        # daemon=True - поток завершается вместе с основным процессом
        # executors - используем ThreadPoolExecutor с 1 потоком для бэкапов
        self.scheduler = BackgroundScheduler(
            daemon=True,
            job_defaults={
                'coalesce': True,           # Объединяет пропущенные запуски в один
                'max_instances': 1,         # Только один экземпляр задачи одновременно
                'misfire_grace_time': 300   # Пропускать задачи, просроченные более 5 минут
            }
        )
        self.backup_dir = "./backups"
        self.max_backups = 10
        self.is_running = False
        self._lock = threading.Lock()  # Защита от параллельных запусков

        # Регистрация функции остановки при выходе из программы
        atexit.register(self._atexit_handler)

    def _atexit_handler(self):
        """Обработчик завершения программы."""
        try:
            self.stop()
        except Exception:
            pass  # Игнорируем любые ошибки при завершении

    def start(self, backup_dir: str = "./backups", frequency: str = "daily",
              hour: int = 23, minute: int = 0, day_of_week: int = 0,
              max_backups: int = 10) -> bool:
        """
        Запуск планировщика с заданными параметрами.

        Args:
            backup_dir: Папка для хранения бэкапов
            frequency: Частота бэкапов (hourly, daily, weekly, monthly)
            hour: Час выполнения (0-23)
            minute: Минута выполнения (0-59)
            day_of_week: День недели для weekly (0=понедельник, 6=воскресенье)
            max_backups: Максимальное количество хранимых бэкапов
        """
        self.backup_dir = backup_dir
        self.max_backups = max_backups

        # Остановка предыдущего планировщика если запущен
        if self.is_running:
            self.stop()

        # Небольшая задержка для гарантированного завершения предыдущего планировщика
        import time
        time.sleep(0.5)

        # Создаём новый планировщик (старый уже shutdown)
        try:
            self.scheduler = BackgroundScheduler(
                daemon=True,
                job_defaults={
                    'coalesce': True,
                    'max_instances': 1,
                    'misfire_grace_time': 300
                }
            )
        except Exception as e:
            app_logger.error(f"Не удалось создать планировщик: {str(e)}")
            return False

        # Настройка триггера в зависимости от частоты
        try:
            if frequency == "hourly":
                trigger = IntervalTrigger(hours=1)
                job_name = "Ежечасное резервное копирование"
            elif frequency == "daily":
                trigger = CronTrigger(hour=hour, minute=minute)
                job_name = f"Ежедневное резервное копирование в {hour:02d}:{minute:02d}"
            elif frequency == "weekly":
                trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
                days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                job_name = f"Еженедельное резервное копирование ({days[day_of_week]}) в {hour:02d}:{minute:02d}"
            elif frequency == "monthly":
                trigger = CronTrigger(day=1, hour=hour, minute=minute)
                job_name = f"Ежемесячное резервное копирование (1-е число) в {hour:02d}:{minute:02d}"
            elif frequency == "test":
                # ТЕСТОВЫЙ РЕЖИМ: запуск через 1 минуту
                now = datetime.now()
                test_time = now.replace(second=0, microsecond=0)
                from datetime import timedelta
                test_time = test_time + timedelta(minutes=1)
                trigger = CronTrigger(
                    hour=test_time.hour,
                    minute=test_time.minute
                )
                job_name = f"Резервное копирование в {test_time.hour:02d}:{test_time.minute:02d}"
            else:
                app_logger.error(f"Неизвестная частота бэкапов: {frequency}")
                return False

            # Добавление задачи
            self.scheduler.add_job(
                self._perform_backup,
                trigger=trigger,
                id='auto_backup',
                name=job_name,
                replace_existing=True
            )

            # Запуск планировщика
            self.scheduler.start()
            self.is_running = True

            app_logger.info(f"Планировщик бэкапов запущен: {job_name}")
            return True

        except Exception as e:
            app_logger.error(f"Ошибка запуска планировщика: {str(e)}")
            return False

    def stop(self):
        """Остановка планировщика."""
        if self.is_running:
            try:
                # wait=False - не ждем завершения текущих задач
                self.scheduler.shutdown(wait=False)
            except Exception:
                pass  # Игнорируем все ошибки при shutdown
            finally:
                self.is_running = False
                app_logger.info("Планировщик бэкапов остановлен")

    def _perform_backup(self):
        """Выполнение резервного копирования с защитой от параллельных запусков."""
        # Защита от параллельных запусков
        if not self._lock.acquire(blocking=False):
            app_logger.warning("Пропуск бэкапа: предыдущий ещё выполняется")
            return

        try:
            # Дополнительная проверка состояния
            if not self.is_running:
                app_logger.warning("Пропуск бэкапа: планировщик остановлен")
                return

            app_logger.info("Начало автоматического резервного копирования...")

            db_session = SessionLocal()
            try:
                result = create_database_backup(self.backup_dir, db_session)
                if result["success"]:
                    app_logger.info(f"Автоматический бэкап создан: {result['path']}")
                    # Очистка старых бэкапов
                    if self.max_backups > 0:
                        cleanup_old_backups(self.backup_dir, self.max_backups)
                else:
                    app_logger.error(f"Ошибка автоматического бэкапа: {result['error']}")
            except Exception as e:
                app_logger.error(f"Критическая ошибка автоматического бэкапа: {str(e)}")
            finally:
                db_session.close()
        finally:
            self._lock.release()

    def run_backup_now(self) -> dict:
        """
        Ручной запуск резервного копирования прямо сейчас.
        Используется для проверки работоспособности.
        """
        app_logger.info("Запуск ручного резервного копирования...")

        # Защита от параллельных запусков
        if not self._lock.acquire(blocking=False):
            return {"success": False, "error": "Резервное копирование уже выполняется"}

        try:
            db_session = SessionLocal()
            try:
                result = create_database_backup(self.backup_dir, db_session)
                if result["success"]:
                    app_logger.info(f"Ручной бэкап создан: {result['path']}")
                    # Очистка старых бэкапов
                    if self.max_backups > 0:
                        cleanup_old_backups(self.backup_dir, self.max_backups)
                    return result
                else:
                    return result
            except Exception as e:
                error_msg = f"Ошибка ручного бэкапа: {str(e)}"
                app_logger.error(error_msg)
                return {"success": False, "error": error_msg}
            finally:
                db_session.close()
        finally:
            self._lock.release()

    def get_status(self) -> dict:
        """Получение статуса планировщика."""
        if not self.is_running:
            return {"running": False, "next_run": None, "job_name": None}

        try:
            job = self.scheduler.get_job('auto_backup')
            if job and job.next_run_time:
                return {
                    "running": True,
                    "next_run": job.next_run_time.strftime("%d.%m.%Y %H:%M:%S"),
                    "job_name": job.name
                }
        except Exception:
            pass
        return {"running": False, "next_run": None, "job_name": None}


# Глобальный экземпляр планировщика
backup_scheduler = BackupScheduler()