"""
    Script to scrape list of top 250 Indian Cities sorted by population.
    Generates a dict mapping city name to state
"""
import json
from urllib2 import urlopen
from bs4 import BeautifulSoup as soup

url = "https://en.wikipedia.org/wiki/List_of_cities_in_India_by_population"
tableclass = "wikitable"
sp = soup(urlopen(url).read(), "html.parser")
tables = sp.find_all("table", attrs={"class": tableclass})

cities = {}
count = 0

for tab in tables:
    for row in tab.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) > 4:
            if count >= 50:
                break
            cities[cells[1].find('a').text] = cells[4].find('a').text
            count += 1

fp = open('cities.json', 'w')
json.dump(cities, fp)
