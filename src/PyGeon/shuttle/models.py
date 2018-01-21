# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class OutsideClicks(models.Model):
    who = models.BigIntegerField(blank=False, primary_key=True)
    where = models.URLField(blank=False)
    when = models.DateTimeField(blank=False)

    def __str__(self):
        return str(self.who) + " " + str(self.when)
