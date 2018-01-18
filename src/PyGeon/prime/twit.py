from twilio.rest import TwilioRestClient
import requests
import tweepy
import json
import datetime
from CONSTANTS import *
from jinja2 import Template
import boto3
import markdown

SENTIMENT_API_ENDPOINT = "http://text-processing.com/api/sentiment/"
# change according to your needs Higher the value, more probability that the tweet is positive
RETWEET_SENTIMENT = 0.65
SMS_PRIORITY_SENTIMENT = 0.50  # change according to your needs
CALL_PRIORITY_SENTIMENT = 0.40  # change according to your needs
RPP = 20  # No. of Tweets to grab per run


# returns positive sentiment probability of a given text
def findSentiment(text):
    r = requests.post(SENTIMENT_API_ENDPOINT, data={'text': text})
    js = json.loads(r.text)
    return js['probability']['pos']


class TwitterClient:
    def __init__(self):
        auth = tweepy.OAuthHandler(
            TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN,
                              TWITTER_ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

    def tweets(self, searchTerm):
        results = self.api.search(searchTerm, count=RPP)
        return results

    def favouriteTweet(self, status_id):
        try:
            self.api.create_favorite(status_id)
        except:
            pass  # Its probably already favourited

    def retweet(self, status_id):
        try:
            self.api.retweet(status_id)
        except:
            pass  # Its probably already retweeted


class SEND:
    # def __init__(self):
    def sendSms(self, sms_text):
        print("Sending SMS " + sms_text)
        try:

            client = boto3.client(
                "sns",
                aws_access_key_id="",
                aws_secret_access_key="",
                region_name="us-east-1"
            )

            client.set_sms_attributes(
                attributes={
                    'DefaultSMSType': 'Transactional'
                }
            )
            list_of_contacts = ["+919551555019"]
            # Create the topic if it doesn't exist (this is idempotent)
            topic = client.create_topic(Name="notifications")
            topic_arn = topic['TopicArn']  # get its Amazon Resource Name

            # Add SMS Subscribers
            for number in list_of_contacts:
                client.subscribe(
                    TopicArn=topic_arn,
                    Protocol='sms',
                    # <-- number who'll receive an SMS message.
                    Endpoint=number
                )
            # Publish a message.
            client.publish(Message=sms_text, TopicArn=topic_arn)
        except:
            print("No Internet")


def email(FROM, TO, SUBJECT, TEXT):
    TEXT = TEXT.replace("\n", "")
    TEXT = TEXT.replace('"', '\"')
    TEXT = TEXT.replace("'", "\'")
    TEXT = str(TEXT).replace('"', "'")
    print ("DEBUG")
    headers = {
        'Authorization': SENDGRID_KEY,
        'Content-Type': 'application/json',
    }
    data = '{"personalizations": [{"to": [{"email": "%s"}]}], "from": {\
                "email": "%s"}, "subject": "%s", "content": [{"type": "text/html", "value": "%s"}]}'
    r = requests.post('https://api.sendgrid.com/v3/mail/send', headers=headers,
                      data=data % (TO, FROM, SUBJECT, str(TEXT)))
    print ("EMAIL DETAILS : ", TO, FROM)
    print (r.reason)
    print (r.status_code)


import functools


class Report:
    def __init__(self, email, hashtag):
        self.TWITTER_HASHTAG = hashtag
        self.FROM_EMAIL_ADDRESS = "sendeexampexample@example.com"
        self.FROM_EMAIL_NAME = "Pygeon"
        self.TO_EMAIL_ADDRESS = email
        self.TO_EMAIL_NAME = "Organiser"

    def generateAnalysis(self, average, sentiments, smsPriorityTweets, callPriorityTweets):
        results = 'Average positive sentiment: ' + str(average) + ' out of ' + str(
            len(sentiments)) + ' tweets. Number of Tweets < ' + str(SMS_PRIORITY_SENTIMENT) + ': ' + str(
            len(smsPriorityTweets)) + '. Number of Tweets < ' + str(CALL_PRIORITY_SENTIMENT) + ': ' + str(len(callPriorityTweets))
        return results

    def generateReport(self, sentiments, smsPriorityTweets, callPriorityTweets):
        average = functools.reduce(
            lambda x, y: x + y, sentiments) / len(sentiments)
        results = self.generateAnalysis(
            average, sentiments, smsPriorityTweets, callPriorityTweets)
        subject = 'Event Bot Alert ' + \
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M")  # + results
        email_text = self.generateEmail(
            callPriorityTweets, smsPriorityTweets, results)
        send = SEND()
        email(self.FROM_EMAIL_ADDRESS, self.TO_EMAIL_ADDRESS, subject,
              email_text)

    def generateEmail(self, callPriorityTweets, smsPriorityTweets, results):
        # Jinja2 Templating Library is used here.
        temptext = open("prime/templates/temp1.html", 'r').read()
        template = Template(temptext)
        emailText = template.render(callPriorityTweets=callPriorityTweets, smsPriorityTweets=smsPriorityTweets, results=[
                                    i.split(": ") for i in results.split(". ")])
        print ("EMAIL: ")
        return emailText

    def send_email_internal(self, from_address, from_name, to_address, to_name, subject, html):
        m = mandrill.Mandrill(MANDRILL_API_KEY)
        message = {
            "from_email": from_address,
            "from_name": from_name,
            "to": [
                {
                    "email": to_address,
                    "name": to_name,
                    "type": "to"
                }
            ],
            "subject": subject,
            "html": html
        }
        result = m.messages.send(message)
        assert len(result) == 1
        result0 = result[0]

        return result0

    def process(self, searchTerm):
        sentiments = []
        smsPriorityTweets = []
        callPriorityTweets = []
        call = False
        twitter = TwitterClient()
        send = SEND()
        results = twitter.tweets(searchTerm)
        for status in results:
            # Favourite the tweet
            twitter.favouriteTweet(status.id)
            # sanitize the tweet
            text = status.text.encode('ascii', 'ignore')
            # find the sentiment
            sentiment = findSentiment(text)
            # ignore the RTs
            if text[0:2] == 'RT':
                continue
            print(text, ' -- ', "%.3f" % sentiment)
            # Retweet the tweet if the sentiment is highly positive
            if sentiment > RETWEET_SENTIMENT:
                twitter.retweet(status.id)

            # send SMS to admins if sentiment is on the negative side
            if sentiment < SMS_PRIORITY_SENTIMENT:
                # add username and sentiment score to the message
                sms_text = '@' + str(status.user.screen_name) + \
                    ': ' + str(text) + ' |SS: ' + str(sentiment)
                send.sendSms(sms_text)
                smsPriorityTweets = smsPriorityTweets + [sms_text]

                # If highly negative, make sure you send a call about the situation.
                if sentiment < CALL_PRIORITY_SENTIMENT:
                    callPriorityTweets = callPriorityTweets + [sms_text]
                    call = True  # sendCall()
                    sms_text = '@' + str(status.user.screen_name) + \
                        ': ' + str(text) + ' |SS: ' + str(sentiment)
                    # send.sendSms(sms_text)
            sentiments = sentiments + [sentiment]
        self.generateReport(sentiments, smsPriorityTweets, callPriorityTweets)
