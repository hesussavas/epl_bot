import datetime

from django.core.management.base import BaseCommand
from lxml import html
from django.conf import settings

from epl_bot.helpers import _parse_bbc_fixture_date
from epl_bot.models import Fixture


class Command(BaseCommand):

    def handle(self, *args, **options):
        tree = html.parse(settings.BBC_FIXTURES_URL)
        table = tree.xpath("//div[@id='fixtures-data']")[0]
        for item in table.getchildren():
            if item.tag == 'h2':
                match_date = _parse_bbc_fixture_date(item.text.strip())
            if item.tag == 'table':
                for match in item.xpath(".//tr[@class='preview']"):
                    home_team = \
                        match.xpath(".//span[@class='team-home teams']")[
                            0].getchildren()[
                            0].text.strip()
                    result = match.xpath(".//abbr[@class='score']")[
                        0].text.strip() if match.xpath(
                        ".//abbr[@class='score']") else ''
                    away_team = \
                        match.xpath(".//span[@class='team-away teams']")[
                            0].getchildren()[
                            0].text.strip()
                    match_kickoff = match.xpath(".//td[@class='kickoff']")[
                        0].text.strip()
                    match_datetime = datetime.datetime.strptime(
                        "{0}T{1}".format(match_date, match_kickoff),
                        "%d-%B-%YT%H:%M")
                    defaults = dict(result=result)
                    Fixture.objects.update_or_create(defaults=defaults,
                                                     match_datetime=match_datetime,
                                                     away_team=away_team,
                                                     home_team=home_team,
                                                     )
