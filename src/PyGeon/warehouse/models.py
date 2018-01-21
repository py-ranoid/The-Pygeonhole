# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import os
from .data import cities, types
import datetime
from exp.settings import TIME_ZONE
import pytz

home = pytz.timezone(TIME_ZONE)

# Create your models here.
"""
Reference :
Models :    https://docs.djangoproject.com/en/2.0/topics/db/models/
Fields :    https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.Field.null

"""


class EventType(models.Model):
    type_id = models.IntegerField(primary_key=True, blank=False, null=False)
    type_name = models.CharField(max_length=20, blank=False, null=False)

    def __str__(self):
        return str(self.type_id) + ": " + str(self.type_name)


class Cities(models.Model):
    city_id = models.CharField(primary_key=True, max_length=4, blank=False)
    city_name = models.CharField(max_length=16, blank=False)

    def __str__(self):
        return self.city_name


class Event(models.Model):
    name = models.TextField(blank=False, null=False)
    webID = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField()  # Start time of the Event
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    organiser = models.TextField(blank=True, null=True)
    organiser_email = models.EmailField(blank=True, null=True)
    organiser_phone = models.BigIntegerField(blank=True, null=True)
    city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, default=None, blank=True, null=True)
    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE, default=None, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    online = models.NullBooleanField(blank=True, null=True, default="True")
    ppool = models.NullBooleanField(blank=True, null=True)
    priority = models.IntegerField(blank=False, default=0)
    img_url = models.URLField(default="NA")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s %s' % (self.id, self.name)


class Subscriber(models.Model):
    fbid = models.BigIntegerField(blank=False)
    event_type = models.ForeignKey(
        EventType, on_delete=models.CASCADE, default=None, blank=True, null=True)
    city = models.ForeignKey(
        Cities, on_delete=models.CASCADE, default=None, blank=True, null=True)


class Log(models.Model):
    fbid = models.BigIntegerField()
    log_type = models.CharField(max_length=10)
    value = models.TextField(blank=False)
    log_time = models.DateTimeField(auto_now_add=True)
    user2bot = models.IntegerField(blank=False, default=1)


def loadCities():
    print "Loading cities:"
    for i in cities:
        print i
        newCity = Cities()
        newCity.city_id = i.get("city_id", None)
        newCity.city_name = i.get("city_name", None)
        if newCity.city_id and newCity.city_name:
            newCity.save()
        del newCity


def loadTypes():
    print "Loading types:"
    for i in types:
        print i
        newType = EventType()
        newType.type_id = i.get("type_id", None)
        newType.type_name = i.get("type_name", None)
        if newType.type_id and newType.type_name:
            newType.save()
        del newType


EVENT_COUNT = Event.objects.all().count()
