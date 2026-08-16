from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Устаревшая команда; архивирование запускает Celery Beat."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "Команда update_schedule больше не выполняет архивирование. "
                "Его запускает Celery Beat по понедельникам в 00:05."
            )
        )
