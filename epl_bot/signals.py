from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from epl_bot.helpers import _check_exact_score, calculate_points_for_results, \
    _check_exact_outcome
from epl_bot.models import Fixture, Bet, Score


@receiver(post_save, sender=Fixture)
def calculate_scores_on_results_writing(sender, instance, **kwargs):
    if instance.result is not None or instance.result != '':
        for bet in Bet.objects.filter(fixture=instance):
            guessed_exact_score = _check_exact_score(instance.result,
                                                     bet.predicted_outcome)
            Score.objects.create(bet=bet,
                                 user_id=bet.user_id,
                                 exact_score=guessed_exact_score,
                                 exact_outcome=False if guessed_exact_score else _check_exact_outcome(
                                     instance.result,
                                     bet.predicted_outcome),
                                 points=calculate_points_for_results(
                                     instance.result,
                                     bet.predicted_outcome))
