# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from warehouse.models import Event, EVENT_COUNT
from home.models import UserFeedback
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse

# Create your views here.
class Hello(View):
    template_name = "home/index.html"

    def get(self, request):
        info = {'evcount': EVENT_COUNT}

        return render(request, self.template_name, info)
        #return render(request, 'frontline/event_query.html', {'evcount': EVENT_COUNT})

def feedReceive(request):
    newFeedback = UserFeedback()

    if request.GET.get("email", None):
        newFeedback.email = request.GET.get("email")
        newFeedback.feedbackcontent = request.GET.get("fbcontent")
        newFeedback.save()

    return HttpResponse("<h1>Your feedback was submitted! Thank you!</h1><a href=\"/home/landing/\">Go back</a>")
