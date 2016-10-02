from django.core.management.base import BaseCommand
from lxml import html
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        tree = html.parse(settings.BBC_RESULTS_URL)
        table = tree.xpath("//div[@id='results-data']")[0]
        for item in table.getchildren():
            if item.tag == 'table':
                for match in item.xpath(".//tr[@class='report']"):
                    home_team = \
                        match.xpath(".//span[@class='team-home teams']")[
                            0].getchildren()[
                            0].text.strip()
                    result = match.xpath(".//abbr[@title='Score']")[
                        0].text.strip().replace('-', ':')
                    away_team = \
                        match.xpath(".//span[@class='team-away teams']")[
                            0].getchildren()[
                            0].text.strip()
                    from epl_bot.models import Fixture
                    fixture = Fixture.objects.filter(away_team=away_team,
                                                     home_team=home_team).last()

                    if fixture and not fixture.result:
                        fixture.result = result
                        fixture.save(force_update=True)
