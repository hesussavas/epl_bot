# -*- coding: utf-8 -*-
import telegram
from lxml import html
from django.conf import settings
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

import re
import datetime

from telegram.ext.callbackqueryhandler import CallbackQueryHandler

from epl_bot.models import Fixture, Team
from epl_bot.settings import FIXTURES_STEP

updater = Updater(token=settings.BOT_TOKEN)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)


echo_handler = MessageHandler([Filters.text], echo)
dispatcher.add_handler(echo_handler)


def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)

caps_handler = CommandHandler('caps', caps, pass_args=True)
dispatcher.add_handler(caps_handler)


def boobs(bot, update):
    buttons = [[telegram.InlineKeyboardButton('Норм', callback_data='1')],
               [telegram.InlineKeyboardButton('Так себе', callback_data='2')],
               [telegram.InlineKeyboardButton('J', callback_data='3')],
               ]
    reply_markup = telegram.InlineKeyboardMarkup(buttons)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Let's see some boobs",
                    reply_markup=reply_markup)


boobs_handler = CommandHandler('boobs', boobs)
dispatcher.add_handler(boobs_handler)


def _parse_bbc_fixture_date(date):
    pattern = re.compile(r'\w+ (\d+)\w+ (\w+) (\d{4})')
    text_date = "-".join(pattern.match(date).groups())
    return text_date


def _parse_fixtures(url):
    tree = html.parse(url)
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

offset = 0
limit = 5


def _get_upcoming_matches(offset=0, limit=5):
    """
    By default returns 5 nearest matches.
    """

    #TODO: add indexes to the returned matches
    now = datetime.datetime.now()
    matches = Fixture.objects.filter(match_datetime__gte=now)[offset:limit]
    return u"\n\n\n".join([unicode(m) for m in matches])


def fixtures(bot, update):

    upcoming_matches = _get_upcoming_matches()
    if upcoming_matches:

        keyboard = [[telegram.InlineKeyboardButton("[]",
                                                   callback_data="1")],
                    [telegram.InlineKeyboardButton("->",
                                                   callback_data="+")]]

        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=upcoming_matches,
                        reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="There is no matches anymore.")


def button(bot, update):
    query = update.callback_query
    global offset, limit
    if query.data == "+":
        offset += FIXTURES_STEP
        limit += FIXTURES_STEP
    elif query.data == "-":
        limit -= FIXTURES_STEP
        offset -= FIXTURES_STEP
    # TODO: make global counting of the upcoming_matches in order to
    # correctly show match numbers and hide -> button after last match
    upcoming_matches = _get_upcoming_matches(offset, limit)
    keyboard = [[telegram.InlineKeyboardButton("<-",
                                               callback_data="-")],
                [telegram.InlineKeyboardButton("[]",
                                               callback_data="1")],
                [telegram.InlineKeyboardButton("->",
                                               callback_data="+")]]
    # modifying keyboard depending on the count of upcoming matches
    if offset <= 0:
        keyboard.pop(0)

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    bot.editMessageText(text=upcoming_matches,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id,
                        reply_markup=reply_markup)


dispatcher.add_handler(CallbackQueryHandler(button))

fixtures_handler = CommandHandler('fixtures', fixtures)
dispatcher.add_handler(fixtures_handler)
