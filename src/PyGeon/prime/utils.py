import requests
import json
import urllib
from prime import sender
from sentry.data import PAGE_ACCESS_TOKEN
# from frontline.views import getUrl
import urllib
from exp.settings import TIME_ZONE
import pytz
home = pytz.timezone(TIME_ZONE)

DEFAULT_URL = 'https://woocommerce.com/wp-content/themes/woo/images/wc-meetups/host-meetup.jpg'
DEFAULT_BUTTON_URL = 'https://www.wikipedia.org'


def getUrl(city=None, type=None, limit=None, startdate=None, enddate=None):
    url = "https://app.cavalier84.hasura-app.io/frontline/all/?"
    params = urllib.urlencode(
        {'city': city, 'type': type, 'start_date': startdate, 'end_date': enddate, 'limit': limit})
    return str(url + params)


def event_presenter(sender_id=None, items=None, send=True, qparams={}):
    if len(items) == 0:
        m = sender.gen_text_message(
            "Sorry, I could not find any events for your query.\nIf I find one, I'll let you know :). \n#ThePyGeonRemembers")
        post_facebook_message(sender_id, m)
    else:
        # print items
        details_list = []
        for ev in items[:10]:
            details_dict = {}
            details_dict['title'] = ev.name
            dur = ev.duration.total_seconds()
            if dur > 0:
                dur = '\n' + str(float(dur / 3600)) + " hours"
            else:
                dur = ''
            print dur
            print ev.duration
            details_dict['subtitle'] = ev.date_time.astimezone(home).strftime("%I:%M%p - %d %b, %y") + \
                dur + '\nBy : ' + ev.organiser
            details_dict['button_text'] = "Open"
            print ev.link
            if '.' in ev.link:
                newurl = "https://app.cavalier84.hasura-app.io/shuttle/bus/?" + \
                    str(urllib.urlencode(
                        {"urlredirect": ev.link, "user": sender_id}))
                details_dict['url'] = newurl
                details_dict['button_url'] = newurl
            else:
                details_dict['url'] = DEFAULT_BUTTON_URL
                details_dict['button_url'] = DEFAULT_BUTTON_URL
            # if ev.img_url == "NA":
            #     details_dict['image_url'] = DEFAULT_URL
            # else:
            #     details_dict['image_url'] = ev.img_url
            details_list.append(details_dict)
            print(details_dict)

        if qparams and len(items) > 10:
            qurl = getUrl(qparams['city'], qparams['evtype'], 30,
                          qparams['start'], qparams['end'])
            details_dict = {
                'title': 'Find more',
                'subtitle': 'Find more events on our website.',
                'button_text': 'Open',
                'url': qurl,
                'button_url': qurl,
            }
            details_list = details_list[:9]
            details_list.append(details_dict)
        print details_list
        if send:
            count = len(items)
            countstr = str(count) if count <= 10 else "10+"
            m = sender.gen_text_message(
                countstr + " events in the upcoming month.")
            post_facebook_message(sender_id, m)
            m = sender.gen_link_cards(details_list)
            post_facebook_message(sender_id, m)
        else:
            return details_list


def post_facebook_message(fbid, message):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": message})
    status = requests.post(post_message_url, headers={
        "Content-Type": "application/json"}, data=response_msg)

    print(status.json())
