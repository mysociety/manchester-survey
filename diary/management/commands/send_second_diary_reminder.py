from django.core.management.base import BaseCommand, CommandError

from diary.models import ReminderManager

class Command(BaseCommand):
    help = 'Sends emails asking people to fill in this weeks diary'


    def handle(self, *args, **options):
        reminders = ReminderManager()
        reminders.send_second_reminder_email()
