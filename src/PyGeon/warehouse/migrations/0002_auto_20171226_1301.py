# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-12-26 13:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetup',
            name='event_ptr',
        ),
        migrations.DeleteModel(
            name='Meetup',
        ),
    ]
