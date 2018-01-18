"""
Handles the watson functions.
Sends the data to watson and recieves back the structured list of entities and intents
"""

import requests
import json
import os
from watson_developer_cloud import ConversationV1

USERNAME = "6fda4b94-d66b-4477-bc2c-ace3915deb72"
PASSWORD = 'HdpxcUU8E3vM'
VERSION = '2017-04-21'


class watson:
    conversation = ""

    def __init__(self):
        """
        Initializing the watson object with watson user credentials
        """
        self.conversation = ConversationV1(
            username=USERNAME,
            password=PASSWORD,
            version=VERSION)

        self.workspace_id = 'ec0ce7a5-3ada-41b8-8c41-e2e02a45df8c'
        if os.getenv("conversation_workspace_id") is not None:
            workspace_id = os.getenv("conversation_workspace_id")

    def sendMessage(self, text):
        """
        sends the message to the watson conversation server and gets json structured response
        :param text: Stores the user input text
        :return: json response from conversation API
        """
        text = " ".join(text.split("\n"))
        response = self.conversation.message(workspace_id=self.workspace_id,
                                             input={'text': text})
        return response


def child_register(data):
    """
    Return the entities
    :param data:The json data that we get from watson conversation
    :return: email and hashtag
    """
    entities = data["entities"]
    email = ""
    hashtag = ""
    if len(entities) < 2:
        return "Input your email address and event #hashtag with the #"
    try:
        for entity in entities:
            if entity["entity"] == "email":
                email = data["input"]["text"][int(
                    entity["location"][0]):int(entity["location"][1])]
            elif entity["entity"] == "hashtag":
                hashtag = data["input"]["text"][int(
                    entity["location"][0]):int(entity["location"][1])]
        return {"hashtag": hashtag, "email": email}
    except:
        return "Input your email address and event #hashtag with the #"


def show_event(data):
    """
    Handles the intent show_event
    :param data: The json data that we get from watson conversation
    :return: information required to make the database query
    """
    entities = data["entities"]
    location = ""
    search_parameter = ""
    result = {}
    date = ""
    for entity in entities:
        if entity["entity"] == "sys-location" or entity["entity"] == "location":
            location = entity["value"].title()
        elif entity["entity"] == "sys-date":
            date = entity["value"]
        elif entity["entity"] == "event_parameter":
            # print(data["input"]["text"])
            search_parameter = data["input"]["text"][int(
                entity["location"][0]):int(entity["location"][1])]

    print(location, date, search_parameter)
    result["date"] = date
    result["location"] = location
    result["search_parameter"] = search_parameter
    return result


def watson_handler(text):
    """
    Takes a text and send it to watson, gets back the data and accordingly calls the functions
    :param text: user input text
    :return: function calls
    """
    conversation = watson()
    data = conversation.sendMessage(text)
    print(data)
    if len(data["intents"]) == 0:
        return "Sorry could understand your query"
    if data["intents"][0]["intent"] == "Show_Events":
        return (show_event(data))
    elif data["intents"][0]["intent"] == "register_event":
        return data["output"]["text"][0]
    elif data["intents"][0]["intent"] == "generate_report":
        return data["output"]["text"][0]
    elif data["intents"][0]["intent"] == "child_register":
        return child_register(data)
    elif data["intents"][0]["intent"] == "greet":
        return data["output"]["text"][0]
    else:
        return data["output"]["text"][0]
