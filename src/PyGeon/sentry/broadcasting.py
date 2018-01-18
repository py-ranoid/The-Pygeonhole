# -*- coding: utf-8 -*-
from warehouse.data import cities, types
import requests
import json
from prime import sender
from prime.utils import event_presenter
from pprint import pprint
from sentry.data import PAGE_ACCESS_TOKEN as LEM_KEY

URL_BROADCAST_CREATE = "https://graph.facebook.com/v2.11/me/message_creatives?access_token=" + LEM_KEY
URL_BROADCAST_SEND = "https://graph.facebook.com/v2.11/me/broadcast_messages?access_token=" + LEM_KEY
URL_TARGET_LABEL_CREATE = "https://graph.facebook.com/v2.11/me/custom_labels?access_token=" + LEM_KEY
# Here the LabelID is also added to the middle of the string.
URL_TARGET_LABEL_ASSOC = "https://graph.facebook.com/v2.11/%s/label?access_token=" + LEM_KEY
URL_TARGET_LABEL_SEND = "https://graph.facebook.com/v2.11/me/broadcast_messages?access_token=" + LEM_KEY
URL_TARGET_LABEL_REMOVE_USER = "https://graph.facebook.com/v2.11/%s/label?access_token=" + \
    LEM_KEY  # Similarly the LabelID is also added here to send to
URL_TARGET_LABEL_RETREIVE = "https://graph.facebook.com/v2.11/%s/custom_labels?access_token=" + LEM_KEY
URL_TARGET_LABEL_KILL = "https://graph.facebook.com/v2.11/%s?access_token=" + LEM_KEY
URL_TARGET_GET_ALL_LABELS = "https://graph.facebook.com/v2.11/me/custom_labels?fields=name&access_token=" + LEM_KEY
DEFAULT_URL = 'https://woocommerce.com/wp-content/themes/woo/images/wc-meetups/host-meetup.jpg'
from warehouse.data import cities, types
labmap = {}
rev_labmap = {}


def add_sub2broad(category, eventid, cityid, fbid):
    print "ADDING USER"
    label_name = get_label_name(eventid, cityid)
    label = get_label(eventid, cityid)
    print label, label_name
    associateUserToLabel(lid=label, upsid=str(fbid))


def fire(ev_set):
    details_list = event_presenter(sender_id=None, items=ev_set, send=False)
    count = len(ev_set)
    countstr = str(count) if count <= 10 else "10+"
    evid = ev_set[0].event_type.type_id
    if int(evid) == 1003:
        cityid = 'NUL'
    else:
        cityid = ev_set[0].city.city_id
    lname = get_label_name(event_id=evid, city_id=cityid)
    labelid = get_label(event_id=evid, city_id=cityid)
    print lname, labelid

    message = countstr + " new " + humanize(cityid, evid)
    mid = createBroadcast(mtype="text", content=message)
    sendTargetBroadcast(msgID=mid, lid=labelid)
    mid = createBroadcast(mtype="template", details=details_list)
    print "Message created with these:"
    print details_list
    sendTargetBroadcast(msgID=mid, lid=labelid)


def createBroadcast(mtype="template", title="Default Title", content="Default Content", image_url="Default Image URL", subtitle="Default Subtitle", url="https://facebook.com/", button_text="Default", payload="DEF::FAKE", details=None):
    """
    Creates a Broadcast message that is stored natively on FB.
    A message ID is returned. This message ID is used to send the message.

    :param mtype = text or template
    :param title = a title string for template message
    :param content = content for a text message
    :param subtitle = a subtitle string for template message
    :param image_url = a image url string for template message
    :param url = a pointing url for template messages
    :param button_text = a list of buttons for template messages
    :param payload = a payload value to return on click for template messages

    msgID is returned.
    """
    tosend = {}
    if mtype == "text":
        tosend = sender.gen_text_message(text=content)
    elif mtype == "template":
        if details is None:
            info = {
                'title': title,
                'image_url': image_url,
                'subtitle': subtitle,
                'url': url,
                'button_text': button_text,
                'payload': payload
            }
            print info
            details = [info]
        tosend = sender.gen_link_cards(details)

    req = requests.post(url=URL_BROADCAST_CREATE, headers={
                        "Content-Type": "application/json"}, data=json.dumps({'messages': [tosend]}))

    if req.status_code == 200:
        return req.json()[u'message_creative_id']
    else:
        print "LOG Server error, response status not 200\n", req.content
        return False


def sendNonTargetBroadcast(msgID=None):
    """
    Sends a non-targetted Broadcast message.
    Message ID is used to send the message.

    :param msgID = The ID of the created messsage.
    """
    if msgID:
        req = requests.post(url=URL_BROADCAST_SEND, headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "message_creative_id": msgID
                            }))
        if req.status_code == 200:
            return req.json()[u'broadcast_id']
            print "LOG Broadcast message sent successfully"
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: No msgID received"
        return False


def createTargetBroadcastLabel(name=None):
    if name:
        req = requests.post(url=URL_TARGET_LABEL_CREATE, headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "name": name
                            }))
        if req.status_code == 200:
            return req.json()["id"]
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: No name received"
        return False


def associateUserToLabel(lid=None, upsid=None):
    if upsid and lid:
        req = requests.post(url=URL_TARGET_LABEL_ASSOC % (lid), headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "user": upsid
                            }))
        if req.status_code == 200:
            return req.json()["success"]
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: Label Name or Upsid not received"
        return False


def humanize(cityid, evid):
    evname = types[int(evid)]['type_name']
    citname = cities[cityid]['city_name']
    if citname == "Online":
        message = "online " + evname + "s"
    else:
        message = evname + "s in " + str(citname)
    return message


def unsubopt_message(cityid, evid):
    message = "You have subscribed to " + humanize(cityid, evid)
    optlist = ["Unsubscribe"]
    payloads = ["UNSUB::" + str(evid) + "::" + str(cityid)]
    m = sender.gen_button_card(message, optlist, payloads)
    return m


def unsubopt_message_long(sublist):
    elements = []
    for evid, cid in sublist:
        elem = {
            'title': humanize(cid, evid),
            'button_text': "Unsubscribe",
            'payload': "UNSUB::" + str(evid) + "::" + str(cid),
        }
        elements.append(elem)
    return elements


def unssociateUserToLabel(lid=None, upsid=None):
    if upsid and lid:
        req = requests.delete(url=URL_TARGET_LABEL_REMOVE_USER % (lid), headers={"Content-Type": "application/json"},
                              data=json.dumps({
                                  "user": upsid
                              }))
        if req.status_code == 200:
            return req.json()["success"]
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: Label Name or Upsid not received"
        return False


def sendTargetBroadcast(msgID=None, lid=None):
    if msgID and lid:
        req = requests.post(url=URL_BROADCAST_SEND, headers={"Content-Type": "application/json"},
                            data=json.dumps({
                                "message_creative_id": msgID,
                                "custom_label_id": lid
                            }))
        if req.status_code == 200:
            print "LOG Target broadcast message sent successfully"
            return req.json()[u'broadcast_id']
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: msgID or lid not received"
        return False


def getLabelsOfUser(psid=None):
    if psid:
        req = requests.get(url=URL_TARGET_LABEL_RETREIVE % (psid))
        if req.status_code == 200:
            return req.json()[u'data']
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: PSID not received"
        return False


def killLabel(lid):
    if lid:
        req = requests.delete(url=URL_TARGET_LABEL_KILL % (lid), headers={
                              "Content-Type": "application/json"}, data="")
        if req.status_code == 200:
            print "LOG The label was successfully murdered.\nHow can you live with yourself?"
            return req.json()[u'success']
        else:
            print "LOG Server error, response status not 200\n", req.content
            return False
    else:
        print "LOG: Label Name not received"
        return False

###############################################


def getLabels():
    req = requests.get(url=URL_TARGET_GET_ALL_LABELS)
    data = []
    if req.status_code == 200:
        data += req.json()[u'data']
        while req.json().get(u'paging', None) and req.json().get(u'paging').get(u'next', None):
            req = requests.get(url=req.json()[u'paging'][u'next'])
            if req.status_code == 200:
                data += req.json()[u'data']
        return data
    else:
        print "LOG Server error, response status not 200\n", req.content
        return False


def get_label_name(event_id, city_id):
    return str(event_id) + "_" + str(city_id) + '_LAB'


def get_label(event_id, city_id):
    return labmap[event_id][city_id]


def get_label_details(lname):
    labparts = lname.split('_')
    return int(labparts[0]), labparts[1]


def unsub(cityid, evid, fbid):
    l = get_label(int(evid), cityid)
    unssociateUserToLabel(l, fbid)
    m = sender.gen_text_message(
        "You have unsubscribed to" + humanize(cityid, evid))
    return m


def gen_labmap():
    for ev_id in types:
        labmap[ev_id] = {}
        if ev_id == 1003:
            labmap[ev_id]['NUL'] = createTargetBroadcastLabel(
                get_label_name(ev_id, 'NUL'))
            continue
        for cid in cities:
            labmap[ev_id][cid] = createTargetBroadcastLabel(
                get_label_name(ev_id, cid))


def killAllLabels(label_results=None):
    if label_results == None:
        label_results = getLabels()
    for i in label_results:
        print "Killing", i['name']
        killLabel(i['id'])


def store_labmap(label_results=None):
    if label_results == None:
        label_results = getLabels()
    for i in label_results:
        name = i['name']
        print i
        rev_labmap[i['id']] = name
        name_parts = name.strip().split('_')
        print name_parts
        if len(name_parts) == 3:
            if labmap.get(int(name_parts[0]), None) is None:
                labmap[int(name_parts[0])] = {}
            labmap[int(name_parts[0])][name_parts[1]] = i['id']


def label_manager(kill=False):
    if kill:
        killAllLabels()
        gen_labmap()
    else:
        labels = getLabels()
        print labels
        if len(labels) >= 19:
            store_labmap(labels)
        else:
            killAllLabels()
            gen_labmap()
    pprint(labmap)


label_manager(False)

###############################################
