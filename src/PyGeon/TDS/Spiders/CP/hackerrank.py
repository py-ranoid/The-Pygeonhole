import feedparser
from datetime import datetime
import pytz
SITE = "hackerrank"
IMAGE = "https://s3.amazonaws.com/sr-marketplace-prod/wp-content/uploads/2015/08/hackerrank.jpg"
from exp.settings import TIME_ZONE
from pprint import pprint
hrhome = pytz.timezone('UTC')
myhome = pytz.timezone(TIME_ZONE)


def scrape():
    """
        Things to extract from each return object (list of dictionaries)
        1. data['name'] =  name of the contest
        2. data['epoch'] =  epoch for time
        3. data['id'] = id of the contest
        4. data['link'] = link of the contest
        :return:
        """
    URL = "https://www.hackerrank.com/calendar/feed.rss"
    d = feedparser.parse(URL)
    data = {}
    try:
        for items in d['entries']:
            name = items['title']
            link = items['href']
            start = datetime.strptime(
                str(items['starttime'])[:-7], '%Y-%m-%d %H:%M')
            end = datetime.strptime(
                str(items['endtime'])[:-7], '%Y-%m-%d %H:%M')
            duration = end - start
            if 'hackerrank' in link:
                data[name] = {'name': name, 'link': link,
                              'time': hrhome.localize(start).astimezone(myhome),
                              'duration': duration}

    except Exception as e:
        print("Something went wrong with hackerrank.scrape!", e)
    return data
