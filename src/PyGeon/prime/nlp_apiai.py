"""
    Script to predict API.ai model's response to an unresolved query.
"""
# cd src/PyGeon/prime
import apiai
import json
from sentry.data import CLIENT_ACCESS_TOKEN
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
from dateutil import parser
context = set()
from time import time

# ignore = {u'input.unknown',
#           u'smalltalk.agent.busy',
#           u'smalltalk.agent.can_you_help',
#           u'smalltalk.agent.chatbot',
#           u'smalltalk.agent.talk_to_me',
#           u'smalltalk.agent.there',
#           u'smalltalk.appraisal.bad',
#           u'smalltalk.appraisal.thank_you',
#           u'smalltalk.confirmation.cancel',
#           u'smalltalk.confirmation.no',
#           u'smalltalk.confirmation.yes',
#           u'smalltalk.emotions.ha_ha',
#           u'smalltalk.greetings.bye',
#           u'smalltalk.greetings.goodmorning',
#           u'smalltalk.greetings.hello',
#           u'smalltalk.greetings.how_are_you',
#           u'smalltalk.greetings.whatsup',
#           u'smalltalk.user.bored',
#           u'smalltalk.user.can_not_sleep',
#           u'smalltalk.user.good',
#           u'smalltalk.user.needs_advice',
#           u'smalltalk.user.tired',
#           u'smalltalk.user.wants_to_talk'}


def primitive_elimination(message):
    if message.strip().lower() in {'hey', 'hi', 'hello', 'are you there'}:
        return {'action': u'smalltalk.greetings.hello',
                'more': False,
                'reply': u'Good day!'}
    else:
        return None


def pred(message, uid, reset=False):
    prim = primitive_elimination(message)
    if prim is not None:
        return prim
    """
        Uses apiai to get response amongst other params.
        Args :
            Message - Text message to be processed.
    """
    request = ai.text_request()
    request.session_id = uid
    request.resetContexts = True if uid not in context else False
    request.query = message
    response = request.getresponse()
    resp = json.loads(response.read())
    result = resp["result"]
    more = result['actionIncomplete']
    params = result['parameters']

    reply = result["fulfillment"]["speech"]
    action = result["action"]
    print "NLP ACTION:", action
    if action == 'Event_found':
        print params
        events = params['Events']
        cities = params['geo-city']
        period = params['Time']
        Dates = params['Date'] if 'Date' in params else ''
        if more:
            if not period and Dates and events and cities:
                context.discard(uid)
                time_block = {
                    'range': False,
                    'dates': [parser.parse(i) for i in Dates]
                }
                return {
                    'more': False,
                    'params': {
                        'city': cities,
                        'time': time_block,
                        'event': events},
                    'reply': "Cool",
                    'action': action
                }
            else:
                context.add(uid)
                return {
                    'more': True,
                    'reply': reply,
                    'action': action
                }
        else:
            context.discard(uid)
            p = period[0]
            periods = p.split('/')
            start = parser.parse(periods[0])
            end = parser.parse(periods[1])
            time_block = {
                'range': True,
                'start': start,
                'end': end
            }
            return {
                'more': False,
                'params': {
                    'city': cities,
                    'time': time_block,
                    'event': events},
                'reply': reply,
                'action': action
            }
    else:
        context.discard(uid)
        return {
            'more': False,
            'reply': reply,
            'action': action
        }


# start = time()
# from pprint import pprint
# pprint(small_pred('I need hackathons in Chennai for next week', 5331))
# pprint(small_pred('Hey', 5331))
# print time() - start
