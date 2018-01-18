import requests
import json
import datetime
import pytz
from exp.settings import TIME_ZONE
home = pytz.timezone(TIME_ZONE)
SITE = "codeforces"
IMAGE = "http://st.codeforces.com/s/32920/images/codeforces-telegram-square.png"


def scrape():
    """
    Things to extract from each return object (list of dictionaries)
    1. data['name'] =  name of the contest
    2. data['epoch'] =  epoch for time
    3. data['id'] = id of the contest
    4. data['link'] = link of the contest
    :return:
    """
    URL = "http://codeforces.com/api/contest.list?gym=false"
    r = requests.get(URL).content
    contests = json.loads(r)['result']
    data = {}
    try:
        for contest in contests:
            if contest['phase'] != 'FINISHED':
                temp = {}
                temp['name'] = contest['name']
                temp['time'] = home.localize(
                    datetime.datetime.fromtimestamp(contest['startTimeSeconds']))
                temp['duration'] = datetime.timedelta(
                    seconds=contest['durationSeconds'])
                temp['link'] = 'http://codeforces.com/contests/' + \
                    str(contest['id'])
                data[contest['id']] = temp
    except Exception as e:
        print("Something went wrong in codeforces.scrape!", e)
    return data
    # scrape_contests()
