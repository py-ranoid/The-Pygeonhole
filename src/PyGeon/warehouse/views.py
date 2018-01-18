from django.views.generic.edit import CreateView
from django.views import generic
from warehouse.models import Event, Cities, EventType
from django.http.response import HttpResponse
from dateutil import parser
from datetime import timedelta
from prime.mailbox import send_simple_message
from prime.way2sms import sendsms
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import render

from exp.settings import TIME_ZONE
import pytz
home = pytz.timezone(TIME_ZONE)
# from


class HackathonCreate(CreateView):
    model = Event
    fields = ["address"]

    # @xframe_options_exempt
    # def get(self, request, *args, **kwargs):
    #     """
    #     Handles GET requests and instantiates a blank version of the form.
    #     """
    #     form_class = self.get_form_class()
    #     form = self.get_form(form_class)
    #     return render(request, 'warehouse/event_form.html', {'form': form})
    #     # return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        newEv = Event()
        print "REQUEST RECEIVED\nPARAMS:"

        params = request.POST

        if params.get("name", None):
            print "Name"
            newEv.name = params.get("name")
        if params.get("type", None):
            print "Type"
            evType = EventType.objects.filter(
                type_id=int(params.get("type")))[0]
            newEv.event_type = evType
        if params.get("description", None):
            print "Desc"
            newEv.description = params.get("description")
        if params.get("link", None):
            print "Link"
            newEv.link = params.get("link")
        if params.get("online", None) is not None:
            print "----", params.get("online", None)
            if params.get("online", None) == "True":
                print "Online"
                newEv.online = True
                newEv.address = ""
                newEv.city = Cities.objects.filter(city_id="NUL")[0]
            else:
                print "Offline"
                newEv.online = False
                if params.get("address", None) and params.get("city", None):
                    print "Offline2"
                    newEv.address = params.get("address")
                    print params.get("city")
                    city = Cities.objects.filter(city_id=params.get("city"))[0]
                    newEv.city = city
        if params.get("pooppool", None):
            print "ppool"
            newEv.ppool = params.get("pooppool")
        if params.get("date", None) and params.get("time", None):
            print "datim"
            dt = str(params.get("date")) + " " + str(params.get("time"))
            newEv.date_time = home.localize(parser.parse(dt))
        if params.get("organiser", None):
            print "org"
            newEv.organiser = params.get("organiser")
        if params.get("organiser_phone", None):
            print "orgp"
            newEv.organiser_phone = params.get("organiser_phone")
        else:
            newEv.organiser_phone = 0
        if params.get("organiser_email", None):
            print "orgn"
            newEv.organiser_email = params.get("organiser_email")

        newEv.duration = timedelta(days=0)
        newEv.priority = -1

        newEv.save()
        send_simple_message('New event added by ' + newEv.organiser, "New Event at http://127.0.0.1:8000/data/" + str(
            newEv.id) + ' \nor https://app.cavalier84.hasura-app.io/data/' + str(newEv.id) + '\n\nVerify here : 127.0.0.1:8000/admin/warehouse/event/?priority=-1')

        return HttpResponse("Your Event has been Recorded. Thank you!")


class DetailsView(generic.DetailView):
    model = Event
    context_object_name = 'i'
