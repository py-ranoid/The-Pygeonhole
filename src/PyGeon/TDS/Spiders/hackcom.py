from dateutil import parser
import urllib2
import ssl
import json
import bs4
import datetime
import random
from exp.settings import TIME_ZONE
import pytz
home = pytz.timezone(TIME_ZONE)


def getHax(city):
    evs = {}
    url = "https://www.hackathon.com/city/india/" + city.lower()
    url.replace(' ', '%20')
    print "LOG: Scraping city:", str(city)
    print "URL:", url
    content = ssl._create_unverified_context()
    resp = urllib2.urlopen(url, context=content)
    soup = bs4.BeautifulSoup(resp.read(), "html.parser")
    results = soup.findAll("div", {"class": "ht-eb-card"})
    for i in results:
        title = i.find("a", {"class": "ht-eb-card__title"})
        site = title.attrs["href"]
        eid = site.split('/')[-1].split('-')[-1]
        resp2 = urllib2.urlopen(site, context=content)
        soup = bs4.BeautifulSoup(resp2.read(), 'html.parser')
        title = soup.h1.text
        organiser = soup.find("div", {"class": "event__organizer"}).a.text
        link = soup.findAll("a", {"class": "button large"})[1]['href']
        place = soup.findAll(
            "div", {"class": "small-10 small-order-2 medium-order-1 columns"})[0].a.text
        dt = parser.parse(soup.findAll("div", {
            "class": "small-10 small-order-2 medium-order-1 columns"})[1].text.split("To")[0].split("From ")[1])
        desc = soup.find("div", {'class': 'event-description__text'}).text
        evstore = {
            'name': title,
            'webid': eid,
            'type': 1001,
            'description': desc,
            'link': link,
            'online': False,
            'city': city,
            'address': "",
            'pooppool': True,
            'datetime': home.localize(dt),
            'organiser': organiser,
        }

        evs[eid] = evstore
    return evs
