import logging

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sets webhook for a bot'

    def handle(self, *args, **options):
        data = dict(url='https://{host}/bot/{token}'.format(host=settings.HOST_NAME,
                                                            token=settings.BOT_TOKEN))
        result = requests.post(
            url='{telegram_url}/bot{token}/setWebhook'.format(
                telegram_url=settings.TELEGRAM_WEBHOOK_URL,
                token=settings.BOT_TOKEN),
            data=data)
        if result.status_code == 200:
            logger.info('Webhook was set succesully')
        else:
            logger.error('Webhook was set UNsuccesully. {}'.format(result.text))