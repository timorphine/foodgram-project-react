import csv

from django.core.management.base import BaseCommand

from recipes.models import Tag

PATH_CSV = '/app/data/tags.csv'


def ingridients_load(row):
    Tag.objects.get_or_create(
        name=row[0],
        slug=row[1],
        color=row[2]
    )


class Command(BaseCommand):
    help = 'Загрузка csv в ДБ'

    def handle(self, *args, **options):
        with open(PATH_CSV, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                ingridients_load(row)
        self.stdout.write('Данные из списка тегов загружены')
