from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from ...models import Weather

import csv

class Command(BaseCommand):
    help = 'csv import command'

    def handle(self, *args, **options):
        f = csv.reader(open('./app/data/data.csv', 'r', encoding='ms932', errors='', newline='' ), delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

        for row in f:
            print(row)

            data = Weather()
            data.date = row[0]
            data.precipitation = row[1]
            data.daylight = row[2]
            data.save()
        
        print('Success!!')