import json
import logging

from django.conf import settings
from django.http.response import HttpResponseForbidden, HttpResponseBadRequest, \
    HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from telegram.update import Update

from epl_bot.handlers import webhook

logger = logging.getLogger(__name__)


class UpdatesRecieveView(View):
    def post(self, request, bot_token):
        if bot_token != settings.BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        raw = request.body.decode('utf-8')
        logger.info(raw)

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            webhook(Update.de_json(payload))
            return HttpResponse('OK')

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(UpdatesRecieveView, self).dispatch(request, *args, **kwargs)
