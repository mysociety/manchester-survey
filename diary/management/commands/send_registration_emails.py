from datetime import date
from django.core.management.base import BaseCommand, CommandError

from diary.models import ReminderManager

class Command(BaseCommand):
    help = 'Sends emails asking people to register for the diary part of the survey'

    def handle(self, *args, **options):
        rm = ReminderManager()
        rm.send_registration_email()
