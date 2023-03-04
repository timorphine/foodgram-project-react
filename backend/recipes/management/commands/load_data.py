import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

PATH_CSV = '/app/data/ingredients.csv'


def ingridients_load(row):
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1]
    )


class Command(BaseCommand):
    help = 'Загрузка csv в ДБ'

    def handle(self, *args, **options):
        with open(PATH_CSV, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                ingridients_load(row)
        self.stdout.write('Данные из списка ингредиентов загружены')
