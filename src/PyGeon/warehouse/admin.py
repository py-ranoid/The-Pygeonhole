# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from models import Event, Cities, EventType, Subscriber, Log
from django.db.models import F
from sentry.broadcasting import fire


def add_pri(modeladmin, request, queryset):
    print "Worked"
    queryset.update(priority=F('priority') + 1)


def botcast(modeladmin, request, queryset):
    print "Worked"
    fire(queryset)


def min_pri(modeladmin, request, queryset):
    print "Worked"
    queryset.update(priority=F('priority') - 1)


def neg_pri(modeladmin, request, queryset):
    print "Worked"
    queryset.update(priority=F('priority') * -1)
    # queryset.update(status='p')


add_pri.short_description = "Add 1 to priority"
min_pri.short_description = "Sub 1 to priority"
neg_pri.short_description = "Negate priority"
botcast.short_description = "Broadcast"


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'priority', 'name', 'webID',
                    'date_time', 'city', 'event_type', 'created_at']
    ordering = ['priority', 'event_type', 'date_time']
    list_filter = ['priority', 'event_type', 'city']
    list_per_page = 20
    actions = [add_pri, min_pri, neg_pri, botcast]


class SubAdmin(admin.ModelAdmin):
    list_display = ['fbid', 'event_type', 'city']
    ordering = ['event_type', 'city']
    list_filter = ['fbid', 'event_type', 'city']
    list_per_page = 20
    # actions = [add_pri, min_pri, neg_pri, botcast]


class EventAdmin2(admin.ModelAdmin):
    list_display = ['id', 'priority']
    ordering = ['priority', 'event_type', 'date_time']
    list_filter = ['priority', 'event_type', 'city']
    actions = []


class LogAdmin(admin.ModelAdmin):
    list_display = ['fbid', 'log_type', 'value', 'log_time']
    ordering = ['log_time']
    list_filter = ['fbid', 'log_type', 'value', 'log_time']
# Register your models here.
# Register your models here.


admin.site.register(Subscriber, SubAdmin)
admin.site.register(Event, EventAdmin)
# admin.site.register(Event, EventAdmin2)
admin.site.register(Cities)
admin.site.register(EventType)
admin.site.register(Log, LogAdmin)
