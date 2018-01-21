import os
import json
import time
from datetime import datetime, timedelta
from warehouse.models import *

from sentry.broadcasting import get_label_details, getLabelsOfUser, unsubopt_message, rev_labmap, unsubopt_message_long, add_sub2broad

from prime import sender
from prime.utils import post_facebook_message

import pytz
from exp.settings import TIME_ZONE
home = pytz.timezone(TIME_ZONE)

# Only three Labels will exist now. (Not very scalable.)
CITY_COLLECTION = 'Cities'
ATTR_COLLECTION = 'Attractions'
SUBA_COLLECTION = 'SubAttractions'


def sublist(fbid):
    unsub_list = []
    userLabels = getLabelsOfUser(fbid)
    if userLabels == False:
        return
    if len(userLabels) == 0:
        message = "You do not have any subscriptions yet."
        m = sender.opt_select(message, ['Subscribe to more events'])
        post_facebook_message(fbid, m)
        return
    message = "You have subscribed to ..."
    m = sender.gen_text_message(message)
    post_facebook_message(fbid, m)
    for l in userLabels:
        print l['id']
        evid, cityid = get_label_details(rev_labmap[l['id']])
        unsub_list.append((evid, cityid))
    elems = unsubopt_message_long(unsub_list)
    print elems
    print len(elems)
    for i in range(len(elems) / 4 + 1):
        print "Index :", i
        print elems[4 * i:4 * (i + 1)]
        batch = elems[4 * i:4 * (i + 1)]
        print len(batch)
        if len(batch) > 1:
            m = sender.gen_list_mainstream(batch)
        else:
            item = batch[0]
            m = sender.gen_button_card(message_text=item['title'],
                                       optlist=[item['button_text']],
                                       payloadlist=[item['payload']])
        post_facebook_message(fbid, m)
        # sublist(1645332865512512)


def add_subscriber_combined(category, eventid, cityid, fbid):
    add_subscriber(category, eventid, cityid, fbid)
    add_sub2broad(category, eventid, cityid, fbid)
    m = unsubopt_message(cityid, eventid)
    post_facebook_message(fbid, m)


def add_subscriber(category, event, city, sender_id):
    # category = "Technology"
    # event = "Developer Meets"
    # city = "Chennai"
    # fbid = 18735873563765
    print category, event, city
    newSub = Subscriber()
    evType = EventType.objects.filter(type_id=int(event))[0]
    city_obj = Cities.objects.filter(city_id=city)[0]
    Subscriber.objects.get_or_create(
        fbid=sender_id,
        event_type=evType,
        city=city_obj
    )


def update_event(ev_id, ev_name=None, ev_webid=None, ev_type=None, ev_desc=None, ev_link=None, ev_online=None, ev_city=None, ev_address=None, ev_ppool=None, ev_date=None, ev_time=None, ev_datetime=None, ev_organiser_name=None, ev_organiser_phone=None, ev_organiser_email=None):
    """
    This function accepts any updates required as induvidual parameters.
    Only provided fields will be updated and the rest will remain as is on the basis of the provided event ID's.

    PLEASE REFER TO THE DOCUMENTATION FOR A SECOND.
    Some parameters must be specific codes from data.json file within warehouse.

    @params:
        @required:
            ev_id - The ID of the row to update
            ev_name - The name of the event
            ev_type - Type of event. NOTE: REFER models.py, data.json in Warehouse for the code to Provide.
            ev_desc - Description of the event.
            ev_link - A URL link to the Event page.
            ev_online - BooleanField for whether the Event is online or not.
            ev_city - City of the event. NOTE: REFER models.py, data.json in Warehouse for the code to Provide.
            ev_address - Address of the venue.
            ev_ppool - BooleanField for whether the Event has a prize pool or not.

            ev_date and ev_time - Either two induvidual date and time params can be provided
            or                  - or a datetime object itself. If data and time are both specified they will be used, otherwise datetime will be used.
            ev_datetime         - The function is different for both, and date_time is preferred.

            ev_organiser_name - The name of the event organiser.
            ev_organiser_email - The Email Address of the organiser.

        @optional:
            ev_organiser_phone - BigIntegerField for event organiser phone number. If not provided default of 0 will be allotted.
    """

    newEv = Event.objects.filter(id=ev_id)[0]
    Event.objects.filter(id=ev_id)[0].delete()
    print "EVENT ADD REQUEST RECEIVED\nPARAMS:"

    if ev_name:
        print "Name"
        newEv.name = ev_name
    if ev_webid:
        print "WebID"
        newEv.webID = ev_webid
    if ev_type:
        print "Type"
        evType = EventType.objects.filter(type_id=int(ev_type))[0]
        newEv.event_type = evType
    if ev_desc:
        print "Desc"
        newEv.description = ev_desc
    if ev_link:
        print "Link"
        newEv.link = ev_link
    if ev_online != None:
        if ev_online:
            print "Online"
            newEv.online = True
            newEv.address = ""
            newEv.city = Cities.objects.filter(city_id="NULL")[0]
        else:
            print "Offline"
            newEv.online = False
            if ev_address and ev_city:
                print "Offline2"
                newEv.address = ev_address
                city = Cities.objects.filter(city_id=ev_city)[0]
                newEv.city = city
    if ev_ppool:
        print "ppool"
        newEv.ppool = ev_ppool
    if ev_datetime:
        print "datim"
        newEv.date_time = ev_datetime
    elif ev_date and ev_time:
        print "datim"
        dt = str(ev_date) + " " + str(ev_time)
        newEv.date_time = parser.parse(dt)
    if ev_organiser_name:
        print "org"
        newEv.organiser = ev_organiser_name
    if ev_organiser_phone:
        print "orgp"
        newEv.organiser_phone = ev_organiser_phone
    else:
        newEv.organiser_phone = 0
    if ev_organiser_email:
        print "orgn"
        newEv.organiser_email = ev_organiser_email

    newEv.duration = timedelta(days=0)
    newEv.save()


def remove_event(ev_id):
    """
    Pretty self-explanatory function. Provide an event_id and the item will be deleted from the database.

    @params:
        @required:
            ev_id - The ID of the record to delete.

    """

    # OnDelete CASCADE has been set. Hence this should work.
    Event.objects.filter(id=ev_id)[0].delete()


def add_event(ev_name=None, ev_webid=None, ev_type=None, ev_desc=None, ev_link=None, ev_online=False, ev_city=None, ev_address=None, ev_ppool=None, ev_date=None, ev_time=None, ev_datetime=None, ev_organiser_name=None, ev_organiser_phone=None, ev_organiser_email=None):
    global EVENT_COUNT
    """
    This function accepts a list of all the necessary parameters to add a new event.
    The absence of any required parameter will crash the function with an Exception.

    PLEASE REFER TO THE DOCUMENTATION FOR A SECOND.
    Some parameters must be specific codes from data.json file within warehouse.

    @params:
        @required:
            ev_name - The name of the event
            ev_type - Type of event. NOTE: REFER models.py, data.json in Warehouse for the code to Provide.
            ev_desc - Description of the event.
            ev_link - A URL link to the Event page.
            ev_online - BooleanField for whether the Event is online or not.
            ev_city - City of the event. NOTE: REFER models.py, data.json in Warehouse for the code to Provide.
            ev_address - Address of the venue.
            ev_ppool - BooleanField for whether the Event has a prize pool or not.

            ev_date and ev_time - Either two induvidual date and time params can be provided
            or                  - or a datetime object itself. If data and time are both specified they will be used, otherwise datetime will be used.
            ev_datetime         - The function is different for both, and date_time is preferred.

            ev_organiser_name - The name of the event organiser.
            ev_organiser_email - The Email Address of the organiser.

        @optional:
            ev_organiser_phone - BigIntegerField for event organiser phone number. If not provided default of 0 will be allotted.
    """

    newEv = Event()
    print "EVENT ADD REQUEST RECEIVED\nPARAMS:"

    if ev_name:
        print "Name"
        newEv.name = ev_name
    if ev_webid:
        print "WebID"
        newEv.webID = ev_webid
    if ev_type:
        print "Type"
        evType = EventType.objects.filter(type_id=int(ev_type))[0]
        newEv.event_type = evType
    if ev_desc:
        print "Desc"
        newEv.description = ev_desc
    if ev_link:
        print "Link"
        newEv.link = ev_link
    if ev_online != None:
        if ev_online:
            print "Online"
            newEv.online = True
            newEv.address = ""
            newEv.city = Cities.objects.filter(city_id="NULL")[0]
        else:
            print "Offline"
            newEv.online = False
            if ev_address and ev_city:
                print "Offline2"
                newEv.address = ev_address
                city = Cities.objects.filter(city_id=ev_city)[0]
                newEv.city = city
    if ev_ppool:
        print "ppool"
        newEv.ppool = ev_ppool

    if ev_datetime:
        print "datim"
        newEv.date_time = home.localize(ev_datetime)
    elif ev_date and ev_time:
        print "datim"
        dt = str(ev_date) + " " + str(ev_time)
        newEv.date_time = home.localize(parser.parse(dt))
    else:
        newEv.date_time = home.localize(datetime(2000, 1, 1))
    if ev_organiser_name:
        print "org"
        newEv.organiser = ev_organiser_name
    if ev_organiser_phone:
        print "orgp"
        newEv.organiser_phone = ev_organiser_phone
    else:
        newEv.organiser_phone = 0
    if ev_organiser_email:
        print "orgn"
        newEv.organiser_email = ev_organiser_email

    newEv.duration = timedelta(days=0)
    print "Event object:"
    print(newEv)
    newEv.save()
    EVENT_COUNT += 1


def add_event_dict(ev_dict):
    global EVENT_COUNT
    """
    This function accepts a list of all the necessary parameters to add a new event.
    The absence of any required parameter will crash the function with an Exception.

    PLEASE REFER TO THE DOCUMENTATION FOR A SECOND.
    Some parameters must be specific codes from data.json file within warehouse.

    @params:
        @required:
            ev_dict - A dictionary with the below given specifications.

    Please note, the keys in the ev_dict parameter must follow this naming standard if you wish to use this function:

        @required:
            ev_name - The name of the event
            ev_type - Type of event. NOTE: REFER models.py, data.json in Warehouse for the code to Provide.
            ev_desc - Description of the event.
            ev_link - A URL link to the Event page.
            ev_online - BooleanField for whether the Event is online or not.
            ev_city - City of the event. NOTE: REFER models.py, data.json in Warehouse for the code to Provide.
            ev_address - Address of the venue.
            ev_ppool - BooleanField for whether the Event has a prize pool or not.

            ev_date and ev_time - Either two induvidual date and time params can be provided
            or                  - or a datetime object itself. If data and time are both specified they will be used, otherwise datetime will be used.
            ev_datetime         - The function is different for both, and date_time is preferred.

            ev_organiser_name - The name of the event organiser.
            ev_organiser_email - The Email Address of the organiser.

        @optional:
            ev_organiser_phone - BigIntegerField for event organiser phone number. If not provided default of 0 will be allotted.
    """

    newEv = Event()
    print "REQUEST RECEIVED\nPARAMS:"

    if ev_dict.get("name", None):
        print "Name", ev_dict.get("name").encode("utf-8")
        newEv.name = ev_dict.get("name").encode("utf-8")
    if ev_dict.get("img", None):
        print "Image", ev_dict.get("img")
        newEv.img_url = ev_dict.get("img")
    else:
        newEv.img_url = "NA"
    if ev_dict.get("webid", None):
        print "WebID", ev_dict.get("webid")
        newEv.webID = ev_dict.get("webid")
    if ev_dict.get("type", None):
        evType = EventType.objects.filter(type_id=int(ev_dict.get("type")))[0]
        print "Type", evType
        newEv.event_type = evType
    if ev_dict.get("description", None):
        print "Desc"
        newEv.description = ev_dict.get("description")
    if ev_dict.get("link", None):
        print "Link", ev_dict.get("link")
        newEv.link = ev_dict.get("link")
    if ev_dict.get("priority", None) is not None:
        print "Priority", ev_dict.get("priority")
        newEv.priority = ev_dict.get("priority")

    # if ev_dict.get("city", None):
    #     print "City"
    #     newEv.city = ev_dict.get("city")

    if ev_dict.get("online", None) is not None:
        if ev_dict.get("online"):
            print "Online", True, Cities.objects.filter(city_id="NUL")[0]
            newEv.online = True
            newEv.address = ""
            newEv.city = Cities.objects.filter(city_id="NUL")[0]
        else:
            print "Offline", ev_dict.get("address")
            newEv.online = False
            if ev_dict.get("address", None):
                print "Offline2"
                newEv.address = ev_dict.get("address")
    if ev_dict.get("city", None):
        city_code = ev_dict.get("city")[:3].upper()
        print "ID :", city_code
        try:
            city = Cities.objects.filter(city_id=city_code)[0]
            newEv.city = city
        except IndexError:
            pass
    if ev_dict.get("pooppool", None) is not None:
        print "ppool", ev_dict.get("pooppool")
        newEv.ppool = ev_dict.get("pooppool")
    if ev_dict.get("date", None) and ev_dict.get("time", None):
        print "datim", home.localize(parser.parse(dt))
        dt = str(ev_dict.get("date")) + " " + str(ev_dict.get("time"))
        newEv.date_time = home.localize(parser.parse(dt))
    if ev_dict.get("datetime", None) is not None:
        print "Datetime", ev_dict.get("datetime")
        dt = ev_dict.get("datetime")
        if dt.tzinfo is not None:
            newEv.date_time = dt
        else:
            newEv.date_time = home.localize(dt)
        print newEv.date_time
    if ev_dict.get("organiser", None):
        print "org", ev_dict.get("organiser")
        newEv.organiser = ev_dict.get("organiser")
    if ev_dict.get("organiser_phone", None):
        print "orgp", ev_dict.get("organiser_phone")
        newEv.organiser_phone = ev_dict.get("organiser_phone")
    else:
        newEv.organiser_phone = 0
    if ev_dict.get("organiser_email", None):
        print "orgn", ev_dict.get("organiser_email")
        newEv.organiser_email = ev_dict.get("organiser_email")
    if ev_dict.get("duration", None) is not None:
        print "duration", ev_dict.get("duration", None)
        newEv.duration = ev_dict.get("duration", None)
    else:
        newEv.duration = timedelta(seconds=0)

    print "=============================="
    # print newEv
    newEv.save()
    EVENT_COUNT += 1
    return newEv


def query(event=None, cid=None, dt_start=None, dt_end=None):
    dt_start = datetime.now() if dt_start is None else dt_start
    span = timedelta(days=30)
    dt_end = dt_start + span if dt_end is None else dt_end
    dt_start = home.localize(dt_start)
    dt_end = home.localize(dt_end)
    print event
    print cid
    print dt_start
    print dt_end
    if cid is None:
        evs = Event.objects.filter(event_type=event).filter(
            date_time__gte=dt_start, date_time__lte=dt_end).extra(order_by=["date_time"])
    else:
        evs = Event.objects.filter(event_type=event).filter(
            city_id=cid).filter(date_time__gte=dt_start, date_time__lte=dt_end).extra(order_by=["date_time"])
    return evs


def getEvCount(evid, citid=None):
    dt_start = datetime.datetime.now()
    dt_start = home.localize(dt_start)
    if citid == None:
        return Event.objects.filter(event_type=evid).filter(date_time__gte=dt_start).count()
    else:
        return Event.objects.filter(event_type=evid, city=citid).filter(date_time__gte=dt_start).count()


def addLog(fbid=0, log_type="Text", value="WubbaLubbaDubDub", u2bot=1):
    l = Log(fbid=fbid, log_type=log_type, value=value, user2bot=u2bot)
    l.save()
#     if not dt_end is None and epoch_end is None:
#         epoch_end = (dt_end - datetime(1970, 1, 1, 0, 0)).total_seconds()
#     if category is None and not event is None:
#         if category in sub_category_list:
#             category = sub_category_list[category][1]
#         try:
#             category = category_map[event]
#         except KeyError:
#             category = 'Developer Meets'
