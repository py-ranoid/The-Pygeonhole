from pprint import pprint
from urllib2 import urlopen
from warehouse import data
from dateutil import parser
import urllib
import datetime
import time
import requests
import json
import re
import pandas as pd
import bs4
import types
import traceback
from prime.data import MEETUPS_API_KEY
from exp.settings import TIMEZONE
import pytz
home = pytz.timezone(TIMEZONE)

searchResultsClass = "searchResults"
contClass = "event-listing-container-li"
descClass = "event-description"
evtInfoClass = "event-info"
rowElementClass = "row"
DEF_ADDR = "Not yet announced."
DEF_DESC = "No Description was provided"

# url = 'https://www.meetup.com/find/?allMeetups=false&keywords=%s&radius=50&userFreeform=%s%2C+India'
# s = soup(urlopen(url).read(), "lxml")
# from pytz import timezone
#
# ind = timezone('Asia/Kolkata')
#
# for container in s.select('.event-listing-container-li'):
#     try:
#         y, m, d = re.findall(
#             '.container-([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})', container.attrs['data-uniqselector'])[0]
#         timestamp = pd.Timestamp(str(d) + '-' + str(m) + '-' + str(y))
#         for events in container.select('.event-listing'):
#             org = events.select('.text--labelSecondary span')[0].text.strip()
#             event_name = events.select('.event')[0].text.strip()
#             attendee_count = events.select(
#                 '.attendee-count')[0].text.strip().split()[0]
#             x = pd.Timestamp(events.select('.text--secondary time')[0].text)
#             x = x.replace(year=int(y), month=int(m), day=int(d))
#             print(x, event_name)
#
#     except Exception as e:
#         print(e)
#
# import pytz
#
# [i for i in pytz.all_timezones if 'Kolkata' in i]
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut
#
#
# """
#     Scrapes meetup pages not more than 30 days old from India
# """
# URL = "https://api.meetup.com"
# # geolocator = Nominatim()
#
# def cities1():
#     """
#     :return: The cities in India Meetup
#     """
#     EXT = "/2/cities?&sign=true&photo-host=public&country=India&page=100"
#     r = requests.get(URL + EXT)
#     response = json.loads(r.text)
#     print(response)
#     citys = []
#     for city in response["results"]:
#         citys.append([city["city"], city["lat"], city["lon"]])
#     # print(citys)
#     return citys
# # cities()
#
#
catmap = {"Technology": 34}

links_scraped = set()


def upcoming_events(category, city, loc):
    global links_scraped
    links_scraped = set()
    evs = {}
    catnum = catmap[category]
    print ("================\n================")
    APIPATH = "/find/upcoming_events"
    """
    Loop throught the offset to get the latest events.
    Stop when you find an event that is already there in the event list
    """
    id_set = set()
    cities = []
    lat_lon = []
    print (city)
    params = {'sign': "true",
              'topic_category': str(catnum),
              'key': MEETUPS_API_KEY,
              'fields': 'featured_photo',
              'photo-host': 'public',
              'lon': str(loc[1]),
              'lat': str(loc[0]),
              'page': '30',
              }
    final_url = URL + APIPATH + '?' + urllib.urlencode(params) + "&&offset="
    for i in range(5):
        print final_url + str(i)
        r = requests.get(final_url + str(i))
        response = json.loads(r.text)
        pprint(response)
        if len(response["events"]) == 0:
            break
        for event in response["events"]:
            evstore = {}
            eid = event['id']
            if eid in id_set:
                continue
            else:
                id_set.add(eid)

            name = event["name"]
            desc = event.get("description", name)
            webinar = False
            if 'webinar' in name.lower():
                webinar = True
            howtofindus = event.get('how_to_find_us', False)
            if not 'local_date' in event or not ('venue' in event or webinar or howtofindus) or not 'group' in event:
                continue

            # TIME DETAILS
            chalu_date = event["local_date"].split("-")
            chalu_time = event["local_time"].split(":")
            dt = datetime.datetime(year=int(chalu_date[0]),
                                   month=int(chalu_date[1]),
                                   day=int(chalu_date[2]),
                                   hour=int(chalu_time[0]),
                                   minute=int(chalu_time[1])
                                   )

            # LOCATION DETAILS
            link = event["link"]
            duration = datetime.timedelta(
                seconds=event.get("duration", 0) / 1000)
            if not webinar:
                address = ""
                if 'venue' in event:
                    address += event[u"venue"].get("address_1", "")
                    address += event[u"venue"].get("address_2", "")
                else:
                    address += howtofindus
            else:
                if howtofindus:
                    address = howtofindus
                else:
                    address = link

            # ORGANISER DETAILS
            groupinfo = event['group']
            if not 'urlname' in groupinfo:
                continue
            organiser = groupinfo['name']

            evstore = {
                'name': name,
                'webid': eid,
                'type': 1002,
                'description': desc,
                'link': link,
                'online': webinar,
                'city': city,
                'address': address,
                'pooppool': False,
                'datetime': dt,
                'organiser': organiser,
            }
            evs[eid] = evstore
    return evs


# URL = "https://www.meetup.com/find/?allMeetups=false&keywords=%s&radius=50&userFreeform=%s%%2C+India"


def group_parser(link='https://www.meetup.com/New-Delhi-R-UseR-Group/'):
    x = bs4.BeautifulSoup(urlopen(link).read(), 'lxml')
    organiser = x.find(
        'a', attrs={'class': 'groupHomeHeader-groupNameLink'}).text
    evs = x.find('ul', attrs={'class': 'groupHome-eventsList-upcomingEvents'})
    if not evs:
        events = x.select('.groupHome-nextMeetup .eventCardHead')
        if events is None:
            return None
    else:
        events = evs.find_all('li')
    events_details = []

    for ev in events[::2]:
        print ev.prettify()
        timestring = ev.select('div.eventTimeDisplay')[0].text
        dtime = parser.parse(timestring)
        main_href = ev.select('a.eventCardHead--title')[0]
        name = main_href.text
        link = main_href.attrs['href']
        ID = link.split('/')[-2]
        print "Name:", name
        print "Organiser:", organiser
        print "Date-Time:", dtime
        print "Link:", link
        print "ID:", ID
        events_details.append({
            'name': name,
            'webid': ID,
            'link': link,
            'datetime': home.localize(dtime),
            'organiser': organiser,
        })
    return events_details


def evlink_parser(URL2, desc_html=True):
    address = ""
    allDescText = None
    if URL2.startswith('/'):
        URL2 = 'https://www.meetup.com' + URL2

    soup = bs4.BeautifulSoup(urlopen(URL2).read(), 'html.parser')

    desc_tag = soup.find("div", attrs={"class": descClass})
    if desc_tag:
        if desc_html:
            description = str(desc_tag)
        else:
            desc_p = desc_tag.findAll("p")
            if desc_p:
                description = '\n'.join([text.text for text in desc_p])
            else:
                description = DEF_DESC
    else:
        description = DEF_DESC

    infoBox = soup.find("div", attrs={"class": evtInfoClass})

    address_tag = infoBox.find("address")
    address = address_tag.text if address_tag is not None else DEF_ADDR

    try:
        start = parser.parse(infoBox.find(
            "span", attrs={"class": "eventTimeDisplay-startDate-time"}).span.text)
        end = parser.parse(infoBox.find(
            "span", attrs={"class": "eventTimeDisplay-endDate-partialTime"}).span.text)
        duration = end - start
    except Exception as e:
        print "Problem while finding Duration :", e
        duration = datetime.timedelta(seconds=0)

    webinar = False

    return {"address": address,
            'pooppool': False,
            'duration': duration,
            'type': 1002,
            'description': description,
            'online': webinar}


def event_target_proc(ID, link_main, id_list):
    global links_scraped
    if '/events/' in link_main:              # Link is an event
        if link_main not in links_scraped:   # Event has been parsed in this session
            links_scraped.add(link_main)
            # print links_scraped
            print ID, link_main
            if ID not in id_list:       # Event is in the DB
                details = evlink_parser(link_main, True)
                return details
            else:
                print ID, "Found in id_list"
        else:
            print ID, "found in scraped links"
    else:
        print link_main, "isn't an event link"
        all_events = []
        # Link is (probably) a group
        group_events = group_parser(link_main)
        if not group_events:
            return None
        for vals in group_events:
            dtime, organiser, name, link, ID = vals
            link = vals['link']
            if '/events/' not in link:
                print "Depth problemo"
            else:
                ev_res = event_target_proc(ID, link, id_list)
                print ev_res, vals
                if ev_res is None:
                    continue
                vals.update(ev_res)
                all_events.append(vals)
                print all_events
        return all_events


def upcoming_events_scraped(category, city, loc, id_list):
    global links_scraped
    links_scraped = set()
    print "list :", id_list
    URL = "https://www.meetup.com/find/events/tech/?allMeetups=false&radius=50&userFreeform=%s%%2C+India"
    ORDERDATE = "&sort=founded_date"
    cittot = 0
    typ = "Developer Meetups"
    cit = city
    evs = {}
    links_scraped = set()
    print "Scraping: ", typ, "in", cit
    print "============================================"
    soup = bs4.BeautifulSoup(urlopen(URL % (cit)).read(), "html.parser")

    print "URL : ", URL % (cit)
    try:
        llist = soup.find("ul", attrs={"class": searchResultsClass}).findAll(
            "li", attrs={"class": contClass})
        if llist:
            for l in llist:
                date = str(l.attrs.get("data-uniqselector")
                           ).split(".container-")[1]
                print ""
                print "DATE: ", date
                print "================================================="
                eventList = l.find("ul").findAll(
                    "li", attrs={"class": rowElementClass})
                if eventList:
                    count = 0
                    for event in eventList:
                        count += 1
                        cittot += 1

                        print "EVENT", count, ":"
                        print "==============================================="

                        try:
                            anchors = event.findAll("a")
                            time = anchors[0].time.text
                            dtime = parser.parse(str(time) + " " + str(date))
                            organiser = anchors[1].span.text
                            name = anchors[2].span.text
                            link = anchors[2].attrs.get("href", None)
                            ID = link.split("/")[-2]
                            print "OUTER LOOP"
                            print "City:", cit
                            print "Name:", name
                            print "Organiser:", organiser
                            print "Date-Time:", dtime
                            print "Link:", link
                            print "ID:", ID
                            res = event_target_proc(ID, link, id_list)
                            print ID, link, res
                            if res is None:
                                continue
                            if isinstance(res, types.ListType):
                                for ev in res:
                                    evstore = {'city': cit}
                                    evstore.update(ev)
                                    ID = evstore['webid']
                                    print evs.get(ID, "NOT"), "exists"
                                    if 'webinar' in evstore['name'].lower():
                                        evstore['online'] = True
                                    evs[evstore['webid']] = evstore
                            else:
                                evstore = {
                                    'name': name,
                                    'webid': ID,
                                    'link': link,
                                    'city': cit,
                                    'datetime': home.localize(dtime),
                                    'organiser': organiser,
                                }
                                evstore.update(res)
                                print evs.get(ID, "NOT"), "exists"
                                if 'webinar' in evstore['name'].lower() or 'webinar' in evstore['address'].lower():
                                    evstore['online'] = True
                                if evstore['online'] == True:
                                    evstore['city'] = 'NUL'
                                evs[evstore['webid']] = evstore

                            # description = ""
                            # address = ""
                            # allDescText = None
                            #
                            # soup = bs4.BeautifulSoup(
                            #     urlopen(URL2).read(), 'html.parser')
                            #
                            # if soup.find("div", attrs={"class": descClass}):
                            #     allDescText = soup.find(
                            #         "div", attrs={"class": descClass}).findAll("p")
                            # infoBox = soup.find(
                            #     "div", attrs={"class": evtInfoClass})
                            #
                            # if allDescText:
                            #     for text in allDescText:
                            #         description += text.text
                            # if infoBox.find("address"):
                            #     address = infoBox.find("address").text
                            #
                            # try:
                            #     start = parser.parse(infoBox.find(
                            #         "span", attrs={"class": "eventTimeDisplay-startDate-time"}).span.text)
                            #     end = parser.parse(infoBox.find(
                            #         "span", attrs={"class": "eventTimeDisplay-endDate-partialTime"}).span.text)
                            #     duration = end - start
                            # except Exception as e:
                            #     print e
                            #     duration = datetime.timedelta(seconds=0)
                            # if address == "":
                            #     address = "Not yet announced."
                            # if description == "":
                            #     description = "No Description was provided"
                            #
                            # webinar = False
                            #
                            # if address.lower().find("webinar") != -1:
                            #     webinar = True

                        except Exception as e:
                            print traceback.print_exc()
                            print e
                            continue

                        # evstore={
                        #     'name': name,
                        #     'webid': ID,
                        #     'type': 1002,
                        #     'description': description,
                        #     'link': link,
                        #     'online': webinar,
                        #     'city': cit,
                        #     'address': address,
                        #     'pooppool': False,
                        #     'datetime': dtime,
                        #     'organiser': organiser,
                        #     'duration': duration
                        # }

        else:
            raise ValueError()
    except Exception as e:
        print e
        print "None Exist!"

    print "============================================"
    print str(cittot), "events in", cit
    return evs


# upcoming_events_scraped("meh", 'Chennai', 0, [])
