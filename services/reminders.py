from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from config import Settings
from database.db import Database


REMINDER_DELTAS = {
    "7_days": timedelta(days=7),
    "3_days": timedelta(days=3),
    "1_day": timedelta(days=1),
}


class ReminderService:
    def __init__(self, bot: Bot, db: Database, settings: Settings):
        self.bot = bot
        self.db = db
        self.settings = settings
        self.scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.timezone))

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    async def schedule_for_user(self, user_id: int) -> None:
        event_dt = self.settings.event_datetime.replace(tzinfo=ZoneInfo(self.settings.timezone))
        now = self._now()

        for reminder_type, delta in REMINDER_DELTAS.items():
            remind_at = event_dt - delta
            if remind_at <= now:
                continue

            job_id = self._job_id(user_id, reminder_type)
            self.scheduler.add_job(
                self._send_reminder_job,
                trigger=DateTrigger(run_date=remind_at),
                id=job_id,
                replace_existing=True,
                kwargs={"user_id": user_id, "reminder_type": reminder_type},
            )
            await self.db.upsert_reminder(
                user_id=user_id,
                reminder_type=reminder_type,
                scheduled_for=remind_at.strftime("%Y-%m-%d %H:%M:%S"),
            )

    async def schedule_for_all_registered_users(self) -> None:
        user_ids = await self.db.get_registered_user_ids()
        for user_id in user_ids:
            await self.schedule_for_user(user_id)

    async def _send_reminder_job(self, user_id: int, reminder_type: str) -> None:
        labels = {
            "7_days": "через 7 дней",
            "3_days": "через 3 дня",
            "1_day": "уже завтра",
        }
        event_time = self.settings.event_datetime.strftime("%d.%m.%Y в %H:%M")
        text = (
            f"Напоминание: мероприятие «{self.settings.event.title}» состоится {event_time}.\n"
            f"Событие {labels.get(reminder_type, 'скоро')}.\n"
            f"Место: {self.settings.event.venue_name}, {self.settings.event.venue_address}."
        )
        try:
            await self.bot.send_message(user_id, text)
            await self.db.mark_reminder_sent(user_id, reminder_type)
        except Exception:
            # Пользователь мог заблокировать бота — для demo-проекта достаточно безопасно пропустить ошибку.
            pass

    @staticmethod
    def _job_id(user_id: int, reminder_type: str) -> str:
        return f"reminder:{user_id}:{reminder_type}"

    def _now(self):
        return datetime.now(tz=ZoneInfo(self.settings.timezone))
