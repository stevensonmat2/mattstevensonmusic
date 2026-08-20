from django.core.management.base import BaseCommand
from django.utils import timezone

from pages.models import DailyVisitor, VisitorCountSnapshot


class Command(BaseCommand):
    help = 'Record the number of unique visitors for today.'

    def handle(self, *args, **options):
        today = timezone.localdate()
        visitor_count = DailyVisitor.objects.filter(day=today).count()
        snapshot = VisitorCountSnapshot.objects.create(visitor_count=visitor_count)
        self.stdout.write(
            self.style.SUCCESS(
                f'Recorded {visitor_count} visitors at {snapshot.checked_at.isoformat()}.',
            ),
        )