import requests
import json
from prime import sender
from sentry.data import PAGE_ACCESS_TOKEN

from exp.settings import TIME_ZONE
import pytz
home = pytz.timezone(TIME_ZONE)

DEFAULT_URL = 'https://woocommerce.com/wp-content/themes/woo/images/wc-meetups/host-meetup.jpg'
DEFAULT_BUTTON_URL = 'https://www.wikipedia.org'


def event_presenter(sender_id=None, items=None, send=True):
    if len(items) == 0:
        m = sender.gen_text_message(
            "Sorry, we could not find any data for your query")
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
                details_dict['url'] = ev.link
                details_dict['button_url'] = ev.link
            else:
                details_dict['url'] = DEFAULT_BUTTON_URL
                details_dict['button_url'] = DEFAULT_BUTTON_URL
            # if ev.img_url == "NA":
            #     details_dict['image_url'] = DEFAULT_URL
            # else:
            #     details_dict['image_url'] = ev.img_url
            details_list.append(details_dict)
            print(details_dict)
        if send:
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
