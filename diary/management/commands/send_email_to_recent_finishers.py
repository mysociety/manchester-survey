from datetime import date
from django.core.management.base import BaseCommand, CommandError

from diary.models import ReminderManager

class Command(BaseCommand):
    args = 'subject template'
    help = 'Sends an email to people who finshed the diary last week'

    def handle(self, *args, **options):
        subject = args[0]
        template = args[1]
        if not subject or not template:
            print 'need subject and template'
        else:
            rm = ReminderManager()
            rm.send_email_to_recently_completed_diary_participants(subject, template)
