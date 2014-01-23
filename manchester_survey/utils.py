from datetime import date, timedelta
from django.utils import dateparse

class SurveyDate:
    def __init__(self, date):
        self.d = date

    def is_diary_day(self):
        if self.d.weekday() > 2:
            return True
        return False

    @classmethod
    def get_week_from_startdate(cls, current, startdate):
        diff = current - startdate
        # convert to weeks
        return ( diff.days / 7 ) + 1

    @classmethod
    def get_start_date(cls, today):
        if today.weekday() == 3:
            return today
        elif today.weekday() < 3:
            add_days = 3 - today.weekday()
        else:
            add_days = ( today.weekday() - 3 ) * -1

        start_day = today + timedelta(days=add_days)
        return start_day
