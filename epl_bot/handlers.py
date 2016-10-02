# -*- coding: utf-8 -*-
import logging
import re

import telegram
from redis.client import StrictRedis
from redis.exceptions import RedisError
from telegram.bot import Bot
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.dispatcher import Dispatcher
from telegram.ext.regexhandler import RegexHandler

from epl_bot.helpers import _get_upcoming_matches
from django.conf import settings

from epl_bot.models import Fixture, Bet, Score

logger = logging.getLogger(__name__)

MATCH, REBET, HOSTS, GUESTS = range(4)
redis = StrictRedis.from_url(settings.REDIS_URL)
match_id = ''


def bet(bot, update):
    upcoming = _get_upcoming_matches(0, 10)
    if upcoming:
        try:
            buttons = [[telegram.KeyboardButton(u"{}. {}".format(i, m.bet_text))]
                       for i, m in enumerate(upcoming, start=1)]
            reply_markup = telegram.ReplyKeyboardMarkup(buttons,
                                                        one_time_keyboard=True)
            bot.sendMessage(chat_id=update.message.chat_id,
                            text="Choose a match to bet:",
                            reply_markup=reply_markup)

            return MATCH

        except Exception as exc:
            logger.warning("EXCEPTION %s: %s", exc, exc.message)
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Currently, there is no matches to bet")


def _get_match_id(match_text):
    regex = ur'^\d+[.] ([A-Za-z 0-9]+) {} ([A-Za-z 0-9]+)$'.format(u"\u26BD")
    m = re.match(regex, match_text)
    if m:
        fixture = Fixture.objects.filter(home_team=m.group(1),
                                         away_team=m.group(2))
        if fixture:
            return fixture[0].id
        else:
            Exception('Wrong match text {}'.format(match_text))
    else:
        raise Exception('Wrong match text {}'.format(match_text))


def match(bot, update):

    global match_id
    match_id = _get_match_id(update.message.text)

    old_bet = Bet.objects.filter(fixture_id=match_id,
                                 user_id=update.message.from_user['id'])
    if old_bet:
        old_score = old_bet[0].predicted_outcome
        message = 'You have already predicted this match: {}. ' \
                  'Do you want to replace your bet?'.format(old_score)
        buttons = [["YES", "NO"]]
        reply_markup = telegram.ReplyKeyboardMarkup(buttons,
                                                    one_time_keyboard=True,
                                                    resize_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=message,
                        reply_markup=reply_markup)
        return REBET
    else:

        buttons = [[telegram.KeyboardButton(str(i)) for i in range(0, 6)],
                   [telegram.KeyboardButton(str(i)) for i in range(6, 11)]]
        reply_markup = telegram.ReplyKeyboardMarkup(buttons,
                                                    one_time_keyboard=True,
                                                    resize_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Enter the hosts score:",
                        reply_markup=reply_markup)

        return HOSTS


def rebet(bot, update):
    if update.message.text == 'YES':
        buttons = [[telegram.KeyboardButton(str(i)) for i in range(0, 6)],
                   [telegram.KeyboardButton(str(i)) for i in range(6, 11)]]
        reply_markup = telegram.ReplyKeyboardMarkup(buttons,
                                                    one_time_keyboard=True,
                                                    resize_keyboard=True)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Enter the hosts score:",
                        reply_markup=reply_markup)

        return HOSTS
    else:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text="See you :)")

        return ConversationHandler.END


def hosts(bot, update):
    # caching hosts bet result for a 1 day - in case of interrupted bet
    # caching is needed to store the whole result after getting both parts of
    # the result: hosts score and guests score
    try:
        redis.set("{user_id}:{match_id}:host".format(
            user_id=update.message.from_user['id'],
            match_id=match_id), update.message.text, settings.REDIS_TTL)
    except RedisError as err:
        logger.error('%s: %s', err.__class__, err.message)
    buttons = [[telegram.KeyboardButton(str(i)) for i in range(0, 6)],
               [telegram.KeyboardButton(str(i)) for i in range(6, 11)]]

    reply_markup = telegram.ReplyKeyboardMarkup(buttons,
                                                one_time_keyboard=True,
                                                resize_keyboard=True)
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Enter the guests score:",
                    reply_markup=reply_markup)

    return GUESTS


def guests(bot, update):
    try:
        host_score = redis.get("{user_id}:{match_id}:host".format(
            user_id=update.message.from_user['id'],
            match_id=match_id))
    except RedisError as err:
        logger.error('%s: %s', err.__class__, err.message)
    guest_score = update.message.text

    predicted_outcome = u"{}:{}".format(host_score, guest_score)
    defaults = dict(predicted_outcome=predicted_outcome)
    Bet.objects.update_or_create(defaults=defaults,
                                 fixture_id=match_id,
                                 user_id=update.message.from_user['id'])
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Well, thanks for betting. "
                         "You've predicted {}".format(predicted_outcome)
                    )

    return ConversationHandler.END


def cancel(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text='Bye! I hope we can talk again some day.')

    return ConversationHandler.END


bet_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('bet', bet)],
    states={
        MATCH: [RegexHandler(
            ur'^(\d+[.] [A-Za-z 0-9]+ {} [A-Za-z 0-9]+)$'.format(u"\u26BD"),
            match)],
        REBET: [RegexHandler(ur'^YES|NO$', rebet)],
        HOSTS: [RegexHandler(ur'^(\d+)$', hosts)],
        GUESTS: [RegexHandler(ur'^(\d+)$', guests)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


def start(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text=u"{}\n"
                         u"Hello! This is bot for betting on football, "
                         u"especially on England Premier League\n {}".format(
                         u"\u26BD"*5,
                         u"\u26BD"*5))


def help(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text=u"Bot supports 2 commands: 1) bet - for making a bet;"
                         u"2) bets - for viewing all your bets")


def bets(bot, update):
    """Returns user's 10 last bets"""

    def choose_bets_prefix(bet):
        if bet.fixture.has_result:
            score = Score.objects.get(user_id=bet.user_id, bet=bet)
            if score.exact_score:
                return u'\U0001f44f'
            elif score.exact_outcome:
                return u'\U0001f44d'
            else:
                return u'\U0001f44e'
        else:
            return u'\u2754'

    user_bets = Bet.objects.filter(
        user_id=update.message.from_user['id']).order_by('-edited_time')[:10]
    results = []

    for bet in user_bets:
        prefix = choose_bets_prefix(bet)
        text = u"{} - {}.\n" \
               u"{} Your bet is {}.".format(
            bet.fixture.home_team,
            bet.fixture.away_team,
            prefix,
            bet.predicted_outcome)
        if bet.fixture.result:
            text += " Outcome is {}".format(bet.fixture.result)
        results.append(text)
    if results:
        res_text = u"\n".join(results)
        header = u"Here is your last {} bets:\n\n".format(len(results))
        bot.sendMessage(update.message.chat_id,
                        text=header+res_text)
    else:
        bot.sendMessage(update.message.chat_id,
                            text="You haven't made any bets yet. "
                                 "Try 'bet' command to place a bet")


def _setup():
    bot = Bot(settings.BOT_TOKEN)
    d = Dispatcher(bot, None, workers=0)

    d.add_handler(CommandHandler("bets", bets))
    d.add_handler(CommandHandler("help", help))
    d.add_handler(CommandHandler("start", start))
    d.add_handler(bet_conv_handler)

    return d

dispatcher = _setup()


def webhook(update):
    dispatcher.process_update(update)