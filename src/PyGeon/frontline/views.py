# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from warehouse.models import Event, EVENT_COUNT
from django.shortcuts import render
from django.views import generic
from warehouse.firebasic import query
from dateutil import parser
import urllib
# Create your views here.


class ListEventsView(ListView):
    model = Event
    paginate_by = 20
    queryset = Event.objects.all()


class EventListView(generic.View):
    def get(self, request, *args, **kwargs):
        # return HttpResponse("Hello World!")
        params = request.GET
        q = Event.objects
        city = params.get("city", None)
        evid = params.get("type", None)
        lim = int(params.get("limit", 30))
        page = int(params.get("page", 1))
        print len(q.all())
        print city, city == "ALL", evid, evid == "ALL"
        if city is not None and not city == "ALL":
            q = q.filter(city_id=city)
            print len(q), city
        if evid is not None and not evid == "ALL":
            q = q.filter(event_type=evid)
            print len(q), evid
        start = parser.parse(str(params.get('start_date', None)))
        end = parser.parse(str(params.get('end_date', None)))
        q = q.filter(date_time__gte=start, date_time__lte=end)
        print len(q)
        paginator = Paginator(q, lim)
        queryset = paginator.page(page)
        page_url = request.build_absolute_uri()[:-1]
        return render(request, 'frontline/event_list.html', {'object_list': queryset, 'city': city, 'evid': evid, 'sdate': params.get('start_date', None), 'edate': params.get('end_date', None), 'pageurl': page_url})

# class EventQuery(generic.View)
