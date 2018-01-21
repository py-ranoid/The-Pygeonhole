import json
import requests
import random
import re
import time
from pprint import pprint
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from django.http.response import HttpResponse
import os
import binascii
from sentry.broadcasting import unsub
from warehouse.data import cities, types
from prime import sender
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt
from warehouse.firebasic import add_subscriber_combined, query, add_event, sublist, getEvCount, addLog
from watson import watson_handler
import datetime
import pytz
from exp.settings import TIME_ZONE
from twit import Report
from prime.utils import event_presenter, post_facebook_message
from nlp_apiai import pred
# Report = twit.Report

# from user_form import temp_dict, User
# cd influx/pygeon/prime
city_wait_flag = {}

template_list, sub_category_list, cities_list = {}, {}, []


def init(fbid):
    """
        Called on clicking Get Started.
        Displays 4 messages and category List.
            Payload on selecting category : SEL1::CategoryTitle
    """
    messages = [
        "Hey. I'm PyGeon.",
        "I can keep you up to speed with events around you.",
    ]
    for i in messages:
        m = sender.gen_text_message(i)
        post_facebook_message(fbid, m)

    event_add_message = "If you're an event organiser,"
    m = sender.gen_button_card(event_add_message, ["Add event here"], [
                               'event.pygeon.tech'], button_type='Links')
    post_facebook_message(fbid, m)
    sub_init(fbid)


def sub_init(fbid):
    optlist = []
    payloadlist = []
    for evid in types:
        evname = types[evid]['type_name']
        title = evname + 's (' + str(getEvCount(evid)) + ')'
        optlist.append(title)
        payloadlist.append("SEL2::" + evname + "::" + "Technology")
    m = sender.gen_button_card(
        "What would you like to subscribe to ?", optlist, payloadlist)
    # m = sender.gen_cards(template_list)
    post_facebook_message(fbid, m)

# def city_prompt(fbid, category, event):
#     question = "Which cities would you like to subscribe these event for ?"
#     q_add = "(Seperate multiple cities by commas.)"
#     m = sender.gen_text_message(
#         "You have chosen " + category + " : " + event + ".")
#     post_facebook_message(fbid, m)
#     m = sender.gen_text_message(question + "\n\n" + q_add)
#     post_facebook_message(fbid, m)
#     city_wait_flag[fbid] = {'status': True,
#                             'category': category, 'event': event}


def city_prompt_temp(fbid, category, event):
    question = "Which cities would you like to subscribe these event for ?"
    m = sender.gen_text_message(question)
    post_facebook_message(fbid, m)
    details = []
    for cid in cities:
        c = cities[cid]
        if cid == 'NUL':
            tt, subtt = 'Online', "Subscribe to Webinars and online meets"
            btext = "Online " + event
        else:
            tt, subtt = c['city_name'], "Subscribe to " + \
                event + " in " + c['city_name']
            btext = event + " in " + c['city_name']
        ec = str(getEvCount(eventmap[event], cid))
        tt += ' (' + ec + ')'
        details.append({
            'title': tt,
            'subtitle': subtt,
            'button_text': btext,
            "payload": "SEL3::" + c['city_name'] + "::" + category + "::" + event})
    m = sender.gen_list_mainstream(details[:4])
    post_facebook_message(fbid, m)
    m = sender.gen_list_mainstream(details[4:8])
    post_facebook_message(fbid, m)


def cityless_proc_temp(fbid, params):
    [cat, event] = params
    evid = eventmap[event]
    add_subscriber_combined(cat, evid, 'NUL', fbid)
    t_start = datetime.datetime.now()
    t_end = t_start + datetime.timedelta(days=30)
    items = query(evid, None, t_start, t_end)
    qparams = {
        'city': 'NUL',
        'evtype': evid,
        'start': t_start,
        'end': t_end
    }
    event_presenter(sender_id=fbid,
                    items=items,
                    send=True,
                    qparams=qparams
                    )


def city_proc_temp(fbid, params):
    [city, cat, event] = params
    print params
    evid = eventmap[event]
    city = "NULL" if city == "Online" else city
    cityid = city[:3].upper()
    add_subscriber_combined(cat, evid, cityid, fbid)
    t_start = datetime.datetime.now()
    t_end = t_start + datetime.timedelta(days=30)
    # event_list = query(event, city, epoch_end)
    items = query(evid, cityid, t_start, t_end)
    qparams = {
        'city': cityid,
        'evtype': evid,
        'start': t_start,
        'end': t_end
    }
    event_presenter(sender_id=fbid,
                    items=items,
                    send=True,
                    qparams=qparams
                    )


# def city_proc(fbid, message="Chennai, Mumbai and Bangalore"):
#     cat = city_wait_flag[fbid]['category']
#     event = city_wait_flag[fbid]['event']
#     parts = re.split(r'(,|and)', message)
#     if len(parts) == 1:
#         cities = [parts[0]]
#         cities = [i for i in cities if i in cities_list]
#     elif len(parts) % 2 == 1:
#         cities = parts[0::2]
#         cities = [i.strip() for i in cities if i.strip() in cities_list]
#     else:
#         return
#     print("Adding Cities ", cities)
#     print(cat, event, fbid)
#     str_fin = "You have subscribed to"
#     for c in cities:
#         add_subscriber_combined(cat, event, c, fbid)
#         str_fin += "\n" + event + "in" + c
#     m = sender.gen_text_message(str_fin)
#     epoch_end = time.time() + 30 * 24 * 60 * 60
#     for c in cities:
#         event_list = query(cat, event, c, epoch_end)
#         if not event_list:
#             m = sender.gen_text_message(
#                 "No" + event + " were found in " + c + "\n We shall keep you updated. :)")
#             continue
#         m = sender.gen_text_message(event + " in " + c + ":")
#         post_facebook_message(fbid, m)
#         details_list = []
#         for ev in event_list[:10]:
#             details_dict = {}
#             details_dict['title'] = ev['name']
#             details_dict['image_url'] = DEFAULT_URL
#             details_dict['subtitle'] = 'By : ' + \
#                                        ev['by'] + "\n" + ev['description']
#             details_dict['url'] = ev['link']
#             details_dict['button_text'] = "Open"
#             details_dict['button_url'] = ev['link']
#             details_list.append(details_dict)
#             print(details_dict)
#         m = sender.gen_link_cards(details_list)
#         post_facebook_message(fbid, m)
#     del city_wait_flag[fbid]


# def form_start(fbid):
#     x = User(fbid)
#     x.start_form()
#     x.proc_form('text', data)


def payloadprocessor(name, fbid):
    """
        #  Processes payloads.
         Splits payloads at ::.
         pname = Payload tag
         add = Payload
    """
    addLog(fbid, "PAYLOAD", name, 1)
    if name == "GET_STARTED_PAYLOAD":
        init(fbid)
        return
    payload_params = name.split("::")
    pname = payload_params[0]
    params = payload_params[1:]
    # if pname == "FORM":
    #     x = temp_dict[fbid]
    #     x.proc_form('payload', params[0])
    print pname
    if pname == "SUB":
        print(params)
        pass
    elif pname == "SEL2":
        evid = eventmap[params[0]]
        if not int(evid) == 1003:
            city_prompt_temp(fbid, params[1], params[0])
        else:
            cityless_proc_temp(fbid, [params[1], params[0]])

    elif pname == "SEL3":
        city_proc_temp(fbid, params)
    elif pname == "UNSUB":
        evid, city = params
        m = unsub(city, evid, fbid)
        post_facebook_message(fbid, m)
    elif pname == "HELP":
        how = params[0]
        if how == "INIT":
            init(fbid)
        elif how == "SUB":
            sublist(fbid)
        elif how == "SEARCH":
            message = "Search for events with queries like \n'Show me Hackathons in Chennai next month', 'Are there any Developer Meetups in Hyderabad next Sunday' and so on..."
            m = sender.gen_text_message(message)
            post_facebook_message(fbid, m)


def df_check(fbid):
    return False


eventmap = {'Developer Meets': 1002,
            'meetups': 1002,
            "Dev. Meet": 1002,
            "Dev. Meets": 1002,
            'hackathon': 1001,
            'Hackathons': 1001,
            'Hackathon': 1001,
            'CP Contests': 1003,
            'CP Contest': 1003,
            'contests': 1003,
            'event': 1001}


def helpdesk(fbid):
    message = "How can I help you ?"
    options = ["Get Started", "My Subscriptions", "Find Events"]
    payloads = ["HELP::INIT", "HELP::SUB", "HELP::SEARCH"]
    m = sender.gen_button_card(message, options, payloads)
    post_facebook_message(fbid, m)


def repolink(fbid):
    text = "Intrigued, much ?\nYou can view our source code here"
    optlist = ['Github Repo']
    linklist = ['https://github.com/py-ranoid/The-Pygeonhole']
    m = sender.gen_button_card(text, optlist, linklist, button_type='Links')
    post_facebook_message(fbid, m)


def feedback(fbid):
    FEEDBACK_LINK = 'https://app.cavalier84.hasura-app.io/#feedback'
    GH_ISSUE_LINK = 'https://github.com/py-ranoid/The-Pygeonhole/issues'
    optlist = ['Drop feedback', 'Raise an issue']

    message = "Would like to request a feature or report an issue ?"
    m = sender.gen_button_card(message, optlist,
                               payloadlist=[FEEDBACK_LINK, GH_ISSUE_LINK],
                               button_type='Links')
    post_facebook_message(fbid, m)


def whattodo(sender_id, message):
    addLog(sender_id, "TEXT", message, 1)
    res = pred(message, sender_id)
    print res
    if not res['more']:
        if res['action'] == 'smalltalk.greetings.hello' or 'get started' in message.lower():
            init(sender_id)
            addLog(sender_id, "ACTION", "INIT", 0)
            return
        elif 'source code' in message.lower() or 'contrib' in message.lower():
            repolink(sender_id)
            addLog(sender_id, "ACTION", "REPOLINK", 0)
            return
        elif res['action'] == 'Sub_init':
            sub_init(sender_id)
            addLog(sender_id, "ACTION", "SUB_INIT", 0)
            return
        elif res['action'] == 'Sub_list':
            sublist(sender_id)
            addLog(sender_id, "ACTION", "SUB_LIST", 0)
            return
        elif res['action'] in {'smalltalk.appraisal.bad', 'smalltalk.confirmation.no', 'smalltalk.agent.bad'}:
            feedback(sender_id)
            addLog(sender_id, "ACTION", "FEEDBACK", 0)
            return
        elif res['action'] == 'smalltalk.agent.can_you_help':
            helpdesk(sender_id)
            addLog(sender_id, "ACTION", "HELPDESK", 0)
            return
        elif not res['action'] == 'Event_found':
            m = sender.gen_text_message(res['reply'])
            addLog(sender_id, "TEXT", res['reply'], 0)
            post_facebook_message(sender_id, m)
            return
        else:
            cities = res['params']['city']
            time_block = res['params']['time']
            events = res['params']['event']
            print "CITIES : ", cities
            print "TIME : ", time_block
            print "EVENTS : ", events
            for c in cities:
                for e in events:
                    if time_block['range']:
                        t_start = time_block['start']
                        t_end = time_block['end']
                        text = "Looking for " + \
                            str(e).title() + ' in ' + str(c) + " from " + \
                            str(t_start) + " to " + str(t_end)
                        m = sender.gen_text_message(text)
                        post_facebook_message(sender_id, m)
                        # print str(c) + ":::" + str(e) + ":::" + str(t_start) + ":::" + str(t_end)
                        items = query(
                            eventmap[e], c[:3].upper(), t_start, t_end)
                        addLog(sender_id, "ACTION", "QUERY::" + text, 0)
                        qparams = {
                            'city': c[:3].upper(),
                            'evtype': eventmap[e],
                            'start': t_start,
                            'end': t_end
                        }
                        event_presenter(sender_id=sender_id,
                                        items=items,
                                        send=True,
                                        qparams=qparams
                                        )
                    else:
                        dates = time_block['dates']
                        for d in dates:
                            text = "Looking for " + \
                                str(e).title() + ' in ' + \
                                str(c) + " on " + str(d)
                            m = sender.gen_text_message(text)
                            post_facebook_message(sender_id, m)

                            t_start = d
                            t_end = t_start + datetime.timedelta(days=1)
                            evid = eventmap[e]
                            cityid = c[:3].upper()
                            items = query(evid, cityid, t_start, t_end)
                            addLog(sender_id, "ACTION", "QUERY::" + text, 0)
                            qparams = {
                                'city': cityid,
                                'evtype': evid,
                                'start': t_start,
                                'end': t_end
                            }
                            event_presenter(sender_id=sender_id,
                                            items=items,
                                            send=True,
                                            qparams=qparams
                                            )
    else:
        reply = res['reply']
        if reply == 'Please add a date or a time period.':
            options = ['Next week', 'Next month', 'This month']
            m = sender.opt_select(reply, options)
        elif reply == 'Where would you like to search for the same ?':
            options = ['Bangalore', 'Chennai', 'Delhi',
                       'Gurgaon',  'Hyderabad', 'Mumbai', 'Pune', 'Online']
            m = sender.opt_select(reply, options)
        elif reply == 'What kind of event are you looking for ?':
            options = ['Hackathons', 'Developer Meets', 'Contests']
            m = sender.opt_select(reply, options)
        else:
            m = sender.gen_text_message(reply)
        addLog(sender_id, "TEXT", "MIDQUERY::" + reply, 0)
        post_facebook_message(sender_id, m)
        return


class BotView(generic.View):
    def get(self, request, *args, **kwargs):
        # return HttpResponse("Hello World!")
        if self.request.GET.get('hub.verify_token', '08081997') == '08081997':
            return HttpResponse(self.request.GET.get('hub.challenge', 'Default'))
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        print('\n\n-------------------------------------------------')
        print "Incoming message"
        pprint(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry.get('messaging', []):
                print "Message :", message
                if 'message' in message:
                    print "'message' found"
                    sender_id = message['sender']['id']
                    data = message['message']
                    print "Sender ID :", sender_id
                    print city_wait_flag
                    if sender_id == u'254026515127873':
                        continue
                    if 'text' in data or 'attachments' in data:
                        if 'text' in data:
                            content = data['text']
                            mtype = 'text'
                        else:
                            content = data['attachments'][0]
                            mtype = 'attachments'
                    else:
                        continue

                    if mtype == 'text':
                        if city_wait_flag.get(sender_id, False):
                            city_proc(sender_id, content)
                        else:
                            whattodo(sender_id, content)
                            return HttpResponse()
                    '''
                    # pprint(data)'''

                elif 'postback' in message:
                    pprint(message)
                    payloadprocessor(
                        message["postback"]["payload"], message["sender"]["id"])
        return HttpResponse()


class SheetsPingView(generic.View):
    def get(self, request, *args, **kwargs):
        # return HttpResponse("Hello World!")
        if self.request.GET.get('hub.verify_token', '08081997') == '08081997':
            return HttpResponse(self.request.GET.get('hub.challenge', 'Default'))
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
