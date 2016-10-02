# -*- coding: utf-8 -*-
import re
import datetime

OUTCOME_VARIANTS = {"home wins": 1,
                    "draw": 2,
                    "away wins": 3}


def _parse_bbc_fixture_date(date):
    pattern = re.compile(r'\w+ (\d+)\w+ (\w+) (\d{4})')
    text_date = "-".join(pattern.match(date).groups())
    return text_date


def _get_upcoming_matches(offset=0, limit=5):
    """
    By default returns 5 nearest matches.
    """

    now = datetime.datetime.now()
    from epl_bot.models import Fixture
    matches = Fixture.objects.filter(match_datetime__gte=now)[offset:limit]
    return matches


def _check_exact_score(actual_score, predicted_score):
    return actual_score == predicted_score


def _check_outcome(result):
    """
    Returns: 1 - home wins
             2 - draw
             3 - away wins
    """
    home, away = result.split(':')
    home, away = int(home), int(away)
    if home == away:
        return OUTCOME_VARIANTS.get('draw')
    elif home < away:
        return OUTCOME_VARIANTS.get('away wins')
    else:
        return OUTCOME_VARIANTS.get('home wins')


def _check_exact_outcome(actual_score, predicted_score):
    return _check_outcome(predicted_score) == _check_outcome(actual_score)


def calculate_points_for_results(actual_score, predicted_score):
    if _check_exact_score(actual_score, predicted_score):
        return 3
    elif _check_exact_outcome(actual_score, predicted_score):
        return 1
    else:
        return 0
