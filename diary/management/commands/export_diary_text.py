from django.core.management.base import BaseCommand, CommandError

from diary.models import ExportManager

class Command(BaseCommand):
    help = 'Spits out one file per uses who has completed diary entries containing all the text based entries ordered by week'

    def handle(self, *args, **options):
        em = ExportManager()
        em.export_diary_text()
