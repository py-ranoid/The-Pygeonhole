def gen_text_message(text):
    return {"text": text}


def gen_attachment(attach):
    return {"attachment": attach}


def gen_cards(details):
    """
    Creates list of cards using Generic Template.
    Buttons lead to postbacks.
    https://developers.facebook.com/docs/messenger-platform/send-messages/template/generic
    Args :
        details : List of elements. (Upto 10)
                    keys : 'title' : 'Heading',
                        'image_url' : 'URL to card image',
                        'subtitle' : 'Description',
                        'url' : 'URL to be opened on clicking image',
                        'button_text' : 'Button Text',
                        'payload' : 'payload value returned on clicking button'
    """
    string = ""
    elements = []
    for i in details:
        elements.append({
                        "title": i['title'], "image_url": i["image_url"], "subtitle": i['subtitle'],
                        "default_action": {
                            "type": "web_url",
                            "url": i['url'],
                            #"messenger_extensions": True,
                            "webview_height_ratio": "tall",
                            #"fallback_url": i.get("fallback_url",i['url'])
                        },
                        "buttons": [
                            # {
                            #   "type":"web_url",
                            #   "url":"https://petersfancybrownhats.com",
                            #   "title":"View Website"
                            # },
                            {
                                "type": "postback",
                                "title": i['button_text'],
                                "payload":i['payload']
                                #"payload":"DEVELOPER_DEFINED_PAYLOAD"
                            }
                        ]
                        })
    return {"attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
    }


def gen_link_cards(details):
    """
    Creates list of cards using Generic Template.
    Buttons open URLs.
    https://developers.facebook.com/docs/messenger-platform/send-messages/template/generic
    Args :
        details : List of elements. (Upto 10)
                    keys : 'title' : 'Heading',
                        'image_url' : 'URL to card image',
                        'subtitle' : 'Description',
                        'url' : 'URL to be opened on clicking image',
                        'button_text' : 'Button Text',
                        'payload' : 'payload value returned on clicking button'
    """

    string = ""
    elements = []
    for i in details:
        elements.append({
                        "title": i['title'],
                        # "image_url": i["image_url"],
                        "subtitle": i['subtitle'],
                        "default_action": {
                            "type": "web_url",
                            "url": i['url'],
                            #"messenger_extensions": True,
                            "webview_height_ratio": "tall",
                            #"fallback_url": i.get("fallback_url",i['url'])
                        },
                        "buttons": [
                            {
                                "type": "web_url",
                                "url": i['button_url'],
                                "title":i['button_text']
                            },
                            # {
                            #     "type":"postback",
                            #     "title":i['button_text'],
                            #     "payload":i['payload']
                            #     #"payload":"DEVELOPER_DEFINED_PAYLOAD"
                            #   }
                        ]
                        })
    return {"attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
    }


def gen_button_card(message_text, optlist, payloadlist, button_type='Postbacks'):
    """
    https://developers.facebook.com/docs/messenger-platform/send-messages/template/button
    """
    print "Gen"
    elements = []
    if button_type == "Postbacks":
        for i in xrange(len(optlist)):
            elements.append({
                "type": "postback",
                "title": optlist[i],
                "payload": payloadlist[i]
            },
            )
    elif button_type == "Links":
        for i in xrange(len(optlist)):
            elements.append({
                "type": "web_url",
                "title": optlist[i],
                "url": payloadlist[i]
            },
            )
    return {"attachment": {
        "type": "template",
        "payload": {
            "template_type": "button",
            "text": message_text,
            "buttons": elements
        }
    }
    }


def opt_select(text, opts):
    #ret_values = opts if ret_values is not None else opts
    # print 'Options are :',opts,'\nPayload is :',ret_values
    quickies = []
    for i in opts:
        quickies.append({
            "content_type": "text",
            "title": i,
            "payload": "DEVELOPER_DEFINED_PAYLOAD"
        })
    return {
        "text": text,
        "quick_replies": quickies,
    }


def gen_list_cards(covertitle, coverimage, coversubtitle, details):
    cover = {
        "title": covertitle, "image_url": coverimage, "subtitle": coversubtitle,
        # "default_action": {
        #   "type": "web_url",
        #   "url": coverurl,
        #   #"messenger_extensions": True,
        #   "webview_height_ratio": "tall",
        #   #"fallback_url": i.get("fallback_url",i['url'])
        # },
        # "buttons":[
        #     {"type":"web_url","url":"https://petersfancybrownhats.com","title":"View Website"},
        #     {   "type":"postback","title":i['button_text'],"payload":i['payload']}
        # ]
    }
    elements = [cover]
    for i in details:
        elements.append({
                        "title": i['title'], "image_url": i["image_url"], "subtitle": i['subtitle'],
                        # "default_action": {
                        #   "type": "web_url",
                        #   "url": i['url'],
                        #   #"messenger_extensions": True,
                        #   "webview_height_ratio": "tall",
                        #   #"fallback_url": i.get("fallback_url",i['url'])
                        # },
                        "buttons": [
                            # {
                            #   "type":"web_url",
                            #   "url":"https://petersfancybrownhats.com",
                            #   "title":"View Website"
                            # },
                            {
                                "type": "postback",
                                "title": i['button_text'],
                                "payload":i['payload']
                                #"payload":"DEVELOPER_DEFINED_PAYLOAD"
                            }
                        ]
                        })
    return {"attachment": {
        "type": "template",
        "payload": {
            "template_type": "list",
            "elements": elements
        }
    }
    }


def gen_list_mainstream(details):
    elements = []
    for i in details:
        elements.append({
                        "title": i['title'],
                        # "image_url": i["image_url"],
                        # "subtitle": i['subtitle'],

                        # "default_action": {
                        #   "type": "web_url",
                        #   "url": i['url'],
                        #   #"messenger_extensions": True,
                        #   "webview_height_ratio": "tall",
                        #   #"fallback_url": i.get("fallback_url",i['url'])
                        # },
                        "buttons": [
                            # {
                            #   "type":"web_url",
                            #   "url":"https://petersfancybrownhats.com",
                            #   "title":"View Website"
                            # },
                            {
                                "type": "postback",
                                "title": i['button_text'],
                                "payload":i['payload']
                                #"payload":"DEVELOPER_DEFINED_PAYLOAD"
                            }
                        ]
                        })
    return {"attachment": {
        "type": "template",
        "payload": {
            "template_type": "list",
            "top_element_style": "compact",
            "elements": elements
        }
    }
    }


def gen_cards_sans_default(details):
    string = ""
    elements = []
    for i in details:
        elements.append({
                        "title": i['title'], "image_url": i["image_url"], "subtitle": i['subtitle'],
                        "buttons": [
                            {
                                "type": "postback",
                                "title": i['button_text'],
                                "payload":i['payload']
                            }
                        ]
                        })
    return {"attachment": {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": elements
        }
    }
    }
