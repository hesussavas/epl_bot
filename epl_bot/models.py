from django.db import models
from django.db.models import fields
from django.db.models.fields.related import ForeignKey


class User(models.Model):
    id = fields.AutoField
    name = fields.TextField(max_length=255,)
    telegram_user_id = fields.IntegerField


class Team(models.Model):
    id = fields.AutoField
    name = fields.TextField(max_length=255, unique=True)
    stadium = fields.TextField(max_length=255)
    logo = fields.BinaryField(null=True, blank=True)


class Fixture(models.Model):
    id = fields.AutoField
    match_datetime = fields.DateTimeField()
    home_team = fields.TextField(max_length=255)
    away_team = fields.TextField(max_length=255)
    result = fields.TextField(null=True, blank=True, default='', max_length=7)

    def __unicode__(self):
        if self.result:
            return u"{home} {result} {away}\n{date}".format(
                home=self.home_team,
                result=self.result,
                away=self.away_team,
                date=self.match_datetime.strftime("%c")
            )
        else:
            return u"{home} {ball_unicode} {away}\n\n{date}".format(
                home=self.home_team,
                ball_unicode=u"\u26BD",
                away=self.away_team,
                date=self.match_datetime.strftime("%c")
            )


class Bet(models.Model):
    id = fields.AutoField
    fixture = ForeignKey(Fixture)
    user = ForeignKey(User)
    predicted_outcome = fields.TextField(max_length=7)

    # user can't bet on the same match twice!
    unique_together = (fixture, user)


class Score(models.Model):
    id = fields.AutoField
    bet = ForeignKey(Bet)
    user = ForeignKey(User)
    exact_score = fields.NullBooleanField(
        help_text="Indicating, whether user've "
                  "predicted an exact result",
        null=True, blank=True)
    exact_outcome = fields.NullBooleanField(
        help_text="Indicating, whether user've predicted an exact outcome",
        null=True, blank=True)
    points = fields.IntegerField(default=0)
