from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile


async def send_materials(bot: Bot, user_id: int, materials_text: str, materials_dir: Path) -> None:
    await bot.send_message(user_id, materials_text)

    candidate_files = [
        materials_dir / "broker_event_kit.txt",
        materials_dir / "broker_event_checklist.txt",
    ]

    for file_path in candidate_files:
        if file_path.exists() and file_path.is_file():
            await bot.send_document(
                user_id,
                FSInputFile(path=file_path),
                caption="Материалы участника мероприятия",
            )
            break
