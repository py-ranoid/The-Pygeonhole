# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-20 09:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0011_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='user2bot',
            field=models.IntegerField(default=1),
        ),
    ]
