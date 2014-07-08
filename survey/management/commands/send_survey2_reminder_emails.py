from datetime import date
from django.core.management.base import BaseCommand, CommandError

from survey.models import InvitationManager

class Command(BaseCommand):
    help = 'Sends emails reminding people to complete survey wave2'

    def handle(self, *args, **options):
        rm = InvitationManager()
        rm.send_survey2_reminder_email()
