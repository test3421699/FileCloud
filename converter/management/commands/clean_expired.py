import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from converter.models import UploadedFile

class Command(BaseCommand):
    help = "Deletes expired files from the database and disk storage"

    def handle(self, *args, **options):
        now = timezone.now()
        # Find all files where the expiration timestamp has passed
        expired_entries = UploadedFile.objects.filter(expires_at__lt=now)
        count = expired_entries.count()

        for entry in expired_entries:
            if entry.file:
                # Delete the physical file from storage
                if os.path.isfile(entry.file.path):
                    os.remove(entry.file.path)
            # Delete the database row
            entry.delete()

        self.stdout.write(self.style.SUCCESS(f"Successfully removed {count} expired files."))
