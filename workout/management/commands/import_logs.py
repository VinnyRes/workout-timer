import os
import csv
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from workout.models import WorkoutLog

class Command(BaseCommand):
    help = "Import workout logs from CSV"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, "data", "import_logs.csv")

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"CSV file not found at {file_path}"))
            return

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Normalize keys (case-insensitive)
                row = {k.strip().lower(): v for k, v in row.items()}

                log = WorkoutLog(
                    name=row.get("name") or row.get("workout") or "Unknown",
                    type=row.get("type", ""),
                    duration=int(row.get("duration", 0) or 0),
                    date_completed=datetime.strptime(
                        row.get("date_completed"), "%Y-%m-%d %H:%M:%S"
                    ),
                )
                log.save()

        self.stdout.write(self.style.SUCCESS("Workout logs imported successfully!"))