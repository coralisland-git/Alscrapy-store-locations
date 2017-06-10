from __future__ import unicode_literals
import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import usaddress

class bellca(scrapy.Spider):
    name = 'bellca'
    domain = ''
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/CA_Cities.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)
        file_path = script_dir + '/geo/US_CA_States.json'
        with open(file_path) as data_file:    
            self.US_CA_States_list = json.load(data_file)

    def start_requests(self):
        for location in self.location_list:
            init_url = 'http://bellca.know-where.com/bellca/cgi/selection?lang=en&loadedApiKey=main&place='+location['city'].split('(')[0].strip()+'%2C+'+self.get_state(location['state'])+'%2C+Canada&ll='+str(location['latitude'])+'%2C'+str(location['longitude'])+'&key=&stype=ll&async=results'
            header = {
                "Accept":"text/html, */*; q=0.01",
                "Accept-Encoding":"gzip, deflate, sdch"
            }
            yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

    def body(self, response):
        print("=========  Checking.......")
        try:
            store_list = response.body.split('<script type="application/ld+json">')
            for store in store_list[1:]:
                store = store.split('</script>')[0].strip()
                store = json.loads(store)
                try:
                    item = ChainItem()
                    item['store_name'] = self.validate(store['name'])
                    item['address'] = self.validate(store['address']['streetAddress'])
                    item['city'] = self.validate(store['address']['addressLocality'])
                    item['state'] = self.validate(store['address']['addressRegion'])
                    item['zip_code'] = self.validate(store['address']['postalCode'])
                    item['country'] = 'Canada'
                    item['phone_number'] = self.validate(store['telephone'])
                    h_temp = ''
                    week_list = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
                    try:
                        hour_list = store['openingHours']
                        for cnt in range(0, len(week_list)):
                            if len(hour_list[cnt]) > 6:
                                if ' ' not in self.validate(hour_list[cnt]):
                                    h_temp += week_list[cnt] + ' ' + self.validate(hour_list[cnt])[:2] + ':' + self.validate(hour_list[cnt])[2:-2] + ':' + self.validate(hour_list[cnt])[-2:] + ', '
                                else:
                                    h_temp += self.validate(hour_list[cnt])[:5] + ':' + self.validate(hour_list[cnt])[5:-2] + ':' + self.validate(hour_list[cnt])[-2:] + ', '
                        item['store_hours'] = h_temp[:-2]
                    except:
                        pass
                    item['store_type'] = self.validate(store['@type'])
                    if item['address']+item['phone_number'] not in self.history:
                        self.history.append(item['address']+item['phone_number'])
                        yield item  
                except:
                    pass  
        except:
            pass

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''

    def eliminate_space(self, items):
        tmp = []
        for item in items:
            if self.validate(item) != '':
                tmp.append(self.validate(item))
        return tmp

    def str_concat(self, items, unit):
        tmp = ''
        for item in items[:-1]:
            if self.validate(item) != '':
                tmp += self.validate(item) + unit
        tmp += self.validate(items[-1])
        return tmp

    def check_country(self, item):
        for state in self.US_CA_States_list:
            if item.lower() in state['abbreviation'].lower():
                return state['country']
        return ''

    def get_state(self, item):
        for state in self.US_CA_States_list:
            if item.lower() in state['name'].lower():
                return state['abbreviation']
        return ''