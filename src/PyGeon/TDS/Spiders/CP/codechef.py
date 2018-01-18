import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import pytz
from exp.settings import TIME_ZONE
home = pytz.timezone(TIME_ZONE)

SITE = "codechef"
IMAGE = 'https://s3.ap-south-1.amazonaws.com/pygeonstatic/CodeChef-logo.jpg'


def scrape():
    """
    Things to extract from each return object (list of dictionaries)
    1. data['name'] =  name of the contest
    2. data['epoch'] =  epoch for time
    3. data['id'] = id of the contest
    4. data['link'] = link of the contest
    :return:
    """
    URL = "https://www.codechef.com/"
    CONTEST_URL = "https://www.codechef.com/contests/"
    r = requests.get(CONTEST_URL).content
    soup = BeautifulSoup(str(r), 'lxml')
    data = {}
    try:
        contest_types = soup.find_all('table', {'class': 'dataTable'})
        # print(contest_types)
        future_cotests = str(contest_types[1])
        future_soup = BeautifulSoup(future_cotests, 'lxml')
        table3 = future_soup.find_all('tr')[1:]
        for item in table3:
            inner_table = BeautifulSoup(str(item), 'lxml')
            tds = inner_table.find_all('td')
            name = tds[1].get_text()
            link = URL + tds[0].get_text()
            start = datetime.strptime(
                tds[2].get_text()[:-3], '%d %b %Y  %H:%M')
            end = datetime.strptime(tds[3].get_text()[:-3], '%d %b %Y  %H:%M')
            data[tds[0].get_text()] = {'name': name,
                                       'link': link,
                                       'time': home.localize(start),
                                       'duration': end - start}
    except Exception as e:
        print("Whoops! something went wrong with scrape contests", e)
    return data

# scrape()
