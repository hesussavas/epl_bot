# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-08 09:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('predicted_outcome', models.TextField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Fixture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_datetime', models.DateTimeField()),
                ('home_team', models.TextField(max_length=255)),
                ('away_team', models.TextField(max_length=255)),
                ('result', models.TextField(blank=True, default=b'', max_length=7, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exact_score', models.NullBooleanField(help_text=b"Indicating, whether user've predicted an exact result")),
                ('exact_outcome', models.NullBooleanField(help_text=b"Indicating, whether user've predicted an exact outcome")),
                ('points', models.IntegerField(default=0)),
                ('bet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='epl_bot.Bet')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=255, unique=True)),
                ('stadium', models.TextField(max_length=255)),
                ('logo', models.BinaryField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='score',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='epl_bot.User'),
        ),
        migrations.AddField(
            model_name='bet',
            name='fixture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='epl_bot.Fixture'),
        ),
        migrations.AddField(
            model_name='bet',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='epl_bot.User'),
        ),
    ]
