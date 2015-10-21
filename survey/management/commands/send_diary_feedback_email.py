from datetime import date
from django.core.management.base import BaseCommand, CommandError

from survey.models import InvitationManager

class Command(BaseCommand):
    help = 'Send an email announcing the results'

    def handle(self, *args, **options):
        rm = InvitationManager()
        rm.send_diary_feedback_email()
