import csv
from django.core.management.base import BaseCommand
from workout.models import WorkoutLog, WorkoutDetail


class Command(BaseCommand):
    help = "Export all workout logs to a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the output CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "type", "duration", "date_completed", "exercise", "kilos", "reps", "sets"])

            for log in WorkoutLog.objects.all().order_by("date_completed"):
                details = WorkoutDetail.objects.filter(workout=log)
                if details.exists():
                    for detail in details:
                        writer.writerow([
                            log.name,
                            log.type,
                            log.duration,
                            log.date_completed,
                            detail.exercise,
                            detail.kilos,
                            detail.reps,
                            detail.sets,
                        ])
                else:
                    writer.writerow([
                        log.name,
                        log.type,
                        log.duration,
                        log.date_completed,
                        "", "", "", ""
                    ])

        self.stdout.write(self.style.SUCCESS(f"Exported logs to {csv_file}"))