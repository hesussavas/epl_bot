from django.apps import AppConfig


class EplBotAppConfig(AppConfig):

    name = 'epl_bot'
    verbose_name = 'Epl Bot'

    def ready(self):
        import epl_bot.signals  # noqa
