import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import base64
from dateutil import relativedelta

def soup(url):
    detailsoup = requests.get(url, headers={"Accept": "application/json"})
    return BeautifulSoup(detailsoup.content, "html.parser")

def clean(string):
    string = ' '.join(string
        .replace('\t', " ")
        .strip()
        .split()
    )
    return string

def clean2(text):
    # rep = {"w": "", "x": "", "y": "", "z": ""}
    # rep = dict((re.escape(k), v) for k, v in rep.items()) 
    # pattern = re.compile("|".join(rep.keys()))
    # return pattern.sub(lambda m: rep[re.escape(m.group(0))], text).lower().replace(" ", '')
    return string_to_base32hex(text).lower()

def base32_to_base32hex(base32_string):
    # Mapping of Base32 characters to Base32Hex characters
    base32_to_base32hex_map = str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567',
        '0123456789ABCDEFGHIJKLMNOPQRSTUV')
    return base32_string.translate(base32_to_base32hex_map)

def string_to_base32hex(input_string):
    # Ensure the string is in bytes
    input_bytes = input_string.encode('utf-8')
    # Encode the bytes in standard Base32
    base32_encoded = base64.b32encode(input_bytes).decode('utf-8')
    # Remove any padding characters
    base32_encoded = base32_encoded.rstrip('=')
    # Convert to Base32Hex
    base32hex_encoded = base32_to_base32hex(base32_encoded)
    return base32hex_encoded

class Event:
    def __init__(self, html, address):
        self.html = html
        self.address = address

    def __str__(self):
        return f"\nName {self.name()} \nDescription {self.description()} \nTickets {self.tickets()} \nDate {self.date()} \nTime {self.time()} \nLocation {self.location()} \nSocial {self.social()}"

    def name(self):
        return clean(self.html.find('div', {'class', 'blueberry-article'}).find('h1').text)
    
    def description(self):
        summary_chunks = self.html.find('div', {'class', 'blueberry-article'}).findAll('div', {'class', 'row'})[4].findAll('p')
        summary = ""
        for x in summary_chunks:
            summary = summary.strip() + " " + x.text
        if len(summary) > 200:
            y = 200
        else:
            y = len(summary)
        return summary[:y] + ' (...)\n' + self.address
    
    def tickets(self):
        try:
            return self.html.find('li', {'class', 'lh-1 icon-tickets'}).text.strip()
        except:
            pass
            
    def date(self):
        dates = self.html.find('li', {'class', 'lh-1 icon-events'}).findAll('time')
        dates_list = []
        for x in dates:
            d1 = datetime.strptime(x['datetime'], "%Y-%m-%dT%H:%M:%SZ").date()
            dates_list.append(d1.isoformat())
            
            if len(dates) == 1:
                dates_list.append((d1 + timedelta(days=1)).isoformat())        
        
        return dates_list
    
    def duration(self):
        dates_list = self.date()
        day1 = datetime.strptime(dates_list[0], "%Y-%m-%d").date()
        day2 = datetime.strptime(dates_list[-1], "%Y-%m-%d").date()
        difference = relativedelta.relativedelta(day2, day1)
        if difference.days < 8 and difference.months == 0 and difference.years == 0:
            return True
        else:
            return False

    def time(self):
        try:
            return clean(self.html.find('li', {'class', 'lh-1 icon-archive'}).text)
        except:
            pass

    def location(self):
        try:
            return clean(self.html.find('li', {'class', 'lh-1 icon-pin'}).find('a')['title'])
        except:
            pass

    def social(self):
        try:
            return self.html.find('li', {'class', 'lh-1 icon-web'}).find('a')['href']
        except:
            pass

def get_events():
    
    url = "https://www.thisisathens.org/events"
    list_of_events = []
    front_page = soup(url)
    last_page = front_page.find('div', {'class', 'events-pager'}).find('li', {'class', 'pager__item pager__item--last-page'}).text
    last_page_int = int(last_page.strip()[-2:].strip())

    for x in range(last_page_int):
        
        page = soup(url + '?page=' + str(x))
        main_block = page.find('div', {'class', 'block block-system block-system-main-block'})
        events = main_block.findAll('article') #Type RecordSet
        
        for event in events:
            address = url + event['about'][7:]
            
            list_of_events.append(Event(soup(address), address))
            
    return list_of_events


list_of_events = get_events()