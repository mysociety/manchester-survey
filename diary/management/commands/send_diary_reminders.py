from datetime import date, timedelta
from django.template import loader, Context, Template
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.management.base import BaseCommand, CommandError
from django.contrib import sites

from survey.models import User

class Command(BaseCommand):
    help = 'Sends emails asking people to fill in this weeks diary'

    def handle(self, *args, **options):
        today = date.today()

        """
        get list of users who are still taking part and where start date is
        not more that 12 weeks ago
        """

        host = sites.models.Site.objects.get_current()
        template = loader.get_template('email/registration_confirm.txt')

        twelve_weeks_ago = today - timedelta(weeks=12)

        users = User.objects.filter(startdate__gte=twelve_weeks_ago).filter(withdrawn=False)

        for user in users:
            context = { 'token': user.token, 'host': host }
            content = template.render(Context(context))
            send_mail('this weeks diary', content, 'test@example.org', [user.email])
