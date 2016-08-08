from django.conf import settings
from django.core.management.base import BaseCommand

from epl_bot.helpers import updater


class Command(BaseCommand):
    help = 'Starts telegram bot'

    def handle(self, *args, **options):
        updater.start_polling()
        updater.idle()
