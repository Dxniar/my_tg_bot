import csv
from pathlib import Path

from database.db import Registration


def export_registrations_to_csv(registrations: list[Registration], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(
            [
                "id",
                "user_id",
                "full_name",
                "phone",
                "email",
                "company",
                "position",
                "city",
                "consent",
                "created_at",
            ]
        )
        for reg in registrations:
            writer.writerow(
                [
                    reg.id,
                    reg.user_id,
                    reg.full_name,
                    reg.phone,
                    reg.email,
                    reg.company,
                    reg.position,
                    reg.city,
                    reg.consent,
                    reg.created_at,
                ]
            )
    return output_path
