import time
from TDS.Spiders import hackcom
from TDS.Spiders import meetup
from warehouse.data import cities
from TDS.Spiders.CP import codechef, codeforces, hackerrank
from warehouse.firebasic import add_event_dict
from warehouse.models import Event
from sentry.broadcasting import fire
import datetime
from pprint import pprint


def job():
    Meetupjob()
    Hackjob()
    CPjob()


def Meetupjob():
    online_queue = []
    for cid in cities:
        meetup_id_set = Event.objects.filter(event_type=1002).filter(
            city=cid).values_list('webID', flat=True)
        all_new = []
        city = cities[cid]
        if cid == 'NUL':
            continue
        evs = meetup.upcoming_events_scraped(
            'Technology', city['city_name'], city['loc'], meetup_id_set)
        for ev_id in evs:
            if not ev_id in meetup_id_set:
                print "\n\nAdding", ev_id
                pprint(evs[ev_id])
                event_details = evs[ev_id]
                event_details['priority'] = 0
                print event_details
                if event_details['online'] == True:
                    online_queue.append(event_details)
                else:
                    all_new.append(add_event_dict(event_details))
        if all_new:
            fire(all_new)
    if online_queue:
        fire(online_queue)


def Hackjob():
    hack_id_set = Event.objects.filter(
        event_type=1001).values_list('webID', flat=True)
    for cid in cities:
        all_new = []
        if cid == 'NUL':
            continue
        city = cities[cid]
        evs = hackcom.getHax(city['city_name'])
        for ev_id in evs:
            if not ev_id in hack_id_set:
                event_details = evs[ev_id]
                event_details['priority'] = 0
                all_new.append(add_event_dict(event_details))
        if all_new:
            fire(all_new)


def CPjob():
    for cpsite in [codechef, codeforces, hackerrank]:
        CPsitejob(cpsite)


def CPsitejob(cpsite):
    site_name = cpsite.SITE
    img_url = cpsite.IMAGE
    print site_name
    id_set = Event.objects.filter(
        organiser=site_name).values_list('webID', flat=True)
    evs = cpsite.scrape()
    all_new = []
    for ev_id in evs:
        if not unicode(ev_id) in id_set:
            event_details = evs[ev_id]
            ev_dict = {
                'name': event_details['name'],
                'priority': 0,
                'datetime': event_details['time'],
                'webid': ev_id,
                'organiser': site_name,
                'link': event_details['link'],
                'duration': event_details['duration'],
                'type': 1003,
                'online': True,
                'img': img_url
            }
            print ev_dict
            all_new.append(add_event_dict(ev_dict))
    if all_new:
        fire(all_new)
