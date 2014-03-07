from datetime import date
from django.core.management.base import BaseCommand, CommandError

from diary.models import ReminderManager

class Command(BaseCommand):
    args = 'user_id'
    help = 'Generates a diary link for a user id'

    def handle(self, *args, **options):
        user_id = args[0]
        print user_id
        rm = ReminderManager()
        rm.generate_link(user_id)
