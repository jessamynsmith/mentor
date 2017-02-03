from django.core.management.base import BaseCommand

from codementor.utils import format_status


class Command(BaseCommand):
    help = 'Display current codementor status'

    def handle(self, *args, **options):
        print(format_status())
