from datetime import date, timedelta
import csv, codecs, cStringIO
from django.utils import dateparse, timezone, encoding

from email.header import Header
from email.utils import formataddr

# Miss out i l o u
digits = "0123456789abcdefghjkmnpqrstvwxyz"

class MistypedIDException(Exception):
    pass

def base32_to_int(s):
    """Convert a base 32 string to an integer"""
    mistyped = False
    if s.find('o')>-1 or s.find('i')>-1 or s.find('l')>-1:
        s = s.replace('o', '0').replace('i', '1').replace('l', '1')
        mistyped = True
    decoded = 0
    multi = 1
    while len(s) > 0:
        decoded += multi * digits.index(s[-1:])
        multi = multi * 32
        s = s[:-1]
    if mistyped:
        raise MistypedIDException(decoded)
    return decoded

def int_to_base32(i):
    """Converts an integer to a base32 string"""
    enc = ''
    while i>=32:
        i, mod = divmod(i,32)
        enc = digits[mod] + enc
    enc = digits[i] + enc
    return enc


class SurveyDate:
    def __init__(self, **kwargs):
        if kwargs.has_key('date'):
            self.d = kwargs['date']

    def is_diary_day(self):
        if self.d.weekday() > 2:
            return True
        return False

    def get_week_from_startdate(self, current, startdate):
        diff = current - startdate
        # convert to weeks
        return ( diff.days / 7 ) + 1

    def get_start_date(self, today):
        if today.weekday() == 3:
            return today
        elif today.weekday() < 3:
            add_days = 3 - today.weekday()
        else:
            add_days = ( today.weekday() - 3 ) * -1

        start_day = today + timedelta(days=add_days)
        return start_day

    # purely for mocking in tests
    @classmethod
    def now(self):
        return timezone.now()

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([encoding.smart_bytes(s,"utf-8",True) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
