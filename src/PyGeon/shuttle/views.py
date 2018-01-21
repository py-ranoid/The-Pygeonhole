# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from shuttle.models import OutsideClicks
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from exp.settings import TIME_ZONE
from warehouse.firebasic import addLog
import datetime
import pytz

home = pytz.timezone("Asia/Kolkata")

# Create your views here.


class Terminal(View):

    def get(self, request):
        return HttpResponse("<html><h1>Oops. Sorry, but the Page you're looking for doesn't exist.</h1></html")


class Bus(View):

    def get(self, request):
        link = request.GET.get(
            "urlredirect", "https://app.cavalier84.hasura-app.io/shuttle/terminal/")
        user = request.GET.get("user")

        if link == "":
            link = "https://app.cavalier84.hasura-app.io/shuttle/terminal/"
        print link
        print user
        addLog(user, "LINK", link, 2)
        return redirect(link)
