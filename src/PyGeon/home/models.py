# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class UserFeedback(models.Model):
    email = models.EmailField(primary_key=True)
    feedbackcontent = models.TextField(blank=False, null=False)

    def __str__(self):
        return (self.email)
