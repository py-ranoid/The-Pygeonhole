import requests
from bs4 import BeautifulSoup
from datetime import datetime


def scrape():
    """
        Things to extract from each return object (list of dictionaries)
        1. data['name'] =  name of the contest
        2. data['epoch'] =  epoch for time
        3. data['id'] = id of the contest
        4. data['link'] = link of the contest
        :return:
    """
    URL = "http://www.spoj.com"
    r = requests.get(URL + "/contests").content
    soup = BeautifulSoup(str(r), 'lxml')
    data = []
    try:
        contest_types = soup.find_all('table', {'class': 'table-condensed'})
        # print(contest_types)
        future_cotests = str(contest_types[0])
        future_soup = BeautifulSoup(future_cotests, 'lxml')
        table3 = future_soup.find_all('tr')[1:]
        for item in table3:
            inner_table = BeautifulSoup(str(item), 'lxml')
            tds = inner_table.find_all('td')
            name = tds[0].get_text()
            link = URL + tds[0].find('a').get('href')
            date = tds[1].find('span').get('title')
            datetime_object = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            epoch = datetime(1970, 1, 1)
            delta_time = int((datetime_object - epoch).total_seconds()) + 19800
            data.append({'name': name, 'link': link, 'epoch': delta_time, 'id': tds[0].find('a').get('href')})
    except Exception as e:
        print("Whoops! something went wrong with scrape spoj", e)
    return data

# print(scrape())
