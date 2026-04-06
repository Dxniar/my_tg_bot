from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class EventConfig:
    title: str = "Форум брокеров и партнёров недвижимости 2026"
    subtitle: str = "Тренды рынка, ипотечные инструменты и новые объекты"
    description: str = (
        "Практический форум для брокеров, агентств и партнёров рынка недвижимости. "
        "Разберём изменения спроса, ипотечные продукты 2026 года, "
        "построим воронки продаж и покажем новые объекты с высоким потенциалом сделок."
    )
    venue_name: str = "Деловой центр «Гранд Плаза»"
    venue_address: str = "Москва, Пресненская наб., 10, зал «Панорама», 5 этаж"
    benefits: str = (
        "• Актуальные рыночные данные и прогнозы\n"
        "• Готовые инструменты для роста конверсии в сделку\n"
        "• Нетворкинг с девелоперами, банками и топ-брокерами\n"
        "• Доступ к материалам и чек-листам для команд"
    )
    program: str = (
        "10:00–10:30 — Регистрация и welcome coffee\n"
        "10:30–11:10 — Аналитика рынка недвижимости 2026\n"
        "11:15–12:00 — Ипотечные инструменты и субсидированные программы\n"
        "12:00–12:40 — Кейсы по работе с клиентами в сегментах comfort/business\n"
        "12:45–13:20 — Презентация новых объектов и спецусловий для партнёров\n"
        "13:20–14:00 — Нетворкинг и ответы на вопросы"
    )
    speakers: str = (
        "• Анна Крылова — коммерческий директор девелопера Skyline Residence\n"
        "• Михаил Громов — руководитель ипотечного направления Банка Нова\n"
        "• Ольга Смирнова — эксперт по брокерским продажам, 14+ лет в отрасли\n"
        "• Павел Чернов — аналитик рынка жилья, автор отраслевых обзоров"
    )
    contacts: str = (
        "Координатор партнёрской программы: Мария Волкова\n"
        "Телефон: +7 (495) 555-24-24\n"
        "Email: partners@grandrealty-events.ru"
    )
    materials_text: str = (
        "Спасибо за регистрацию!\n\n"
        "Вот материалы участника:\n"
        "1) Презентация по трендам и спросу\n"
        "2) Чек-лист брокера по подготовке клиента к сделке\n"
        "3) Партнёрские условия по новым объектам\n\n"
        "Полезные ссылки:\n"
        "• https://www.cbr.ru/statistics/\n"
        "• https://наш.дом.рф/\n"
        "• https://rosreestr.gov.ru/"
    )


def _parse_admin_ids(raw: str) -> list[int]:
    if not raw.strip():
        return []
    result: list[int] = []
    for value in raw.split(","):
        value = value.strip()
        if value.isdigit():
            result.append(int(value))
    return result


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: list[int]
    database_path: Path
    event_datetime: datetime
    timezone: str
    webhook_base_url: str
    webhook_path: str
    webhook_secret: str | None
    webapp_host: str
    webapp_port: int
    event: EventConfig



def load_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "")
    if not bot_token:
        raise ValueError("Переменная BOT_TOKEN не задана. Добавьте её в .env")

    database_path = Path(os.getenv("DATABASE_PATH", "database/event_bot.db"))
    event_datetime_str = os.getenv("EVENT_DATETIME", "2026-09-25 10:00")
    event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")

    webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
    if not webhook_path.startswith("/"):
        webhook_path = f"/{webhook_path}"

    return Settings(
        bot_token=bot_token,
        admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
        database_path=database_path,
        event_datetime=event_datetime,
        timezone=os.getenv("TIMEZONE", "Europe/Moscow"),
        webhook_base_url=os.getenv("WEBHOOK_BASE_URL", "https://example.com"),
        webhook_path=webhook_path,
        webhook_secret=(os.getenv("WEBHOOK_SECRET", "").strip() or None),
        webapp_host=os.getenv("WEBAPP_HOST", "0.0.0.0"),
        webapp_port=int(os.getenv("WEBAPP_PORT", "8080")),
        event=EventConfig(),
    )
