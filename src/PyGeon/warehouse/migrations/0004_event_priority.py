# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-01 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0003_subscriber'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='priority',
            field=models.IntegerField(default=0),
        ),
    ]
