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
import datetime

class Peispider(scrapy.Spider):
    name = "peispider"
    domain = ''
    history = []

    def __init__(self, *args, **kwargs):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_Cities.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self):
        for location in self.location_list:
            header = {
                "Accept":"application/json, text/plain, */*",
                "Accept-Encoding":"gzip, deflate, br"
            }
            init_url  = 'https://www.peiwei.com/api/location/storesByCoordinates?lat='+str(location['latitude'])+'&lon='+str(location['longitude'])+'&radius=100'
            yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

    def body(self, response):
        try:
            store_list = json.loads(response.body)['Stores']
            for store in store_list:
                try:
                    item = ChainItem()
                    item['store_name'] = store['Description']
                    item['store_number'] = ''
                    item['address'] = store['Address1']
                    item['address2'] = store['Address2']
                    item['city'] = store['City']
                    item['state'] = store['State']
                    item['zip_code'] = store['Zip']
                    item['country'] = 'United States'
                    item['phone_number'] = store['Phone']
                    item['latitude'] = store['Latitude']
                    item['longitude'] = store['Longitude']
                    try:
                        time1_close = store['OperatingHours'][0]['ClosingTime'][6:-2]
                        time1_close = datetime.datetime.utcfromtimestamp(int(int(time1_close)/1000))
                        time1_open = store['OperatingHours'][0]['OpeningTime'][6:-2]
                        time1_open = datetime.datetime.utcfromtimestamp(int(int(time1_open)/1000))
                        time2_close = store['OperatingHours'][6]['ClosingTime'][6:-2]
                        time2_close = datetime.datetime.utcfromtimestamp(int(int(time2_close)/1000))
                        time2_open = store['OperatingHours'][6]['OpeningTime'][6:-2]
                        time2_open = datetime.datetime.utcfromtimestamp(int(int(time2_open)/1000))
                        time1 = "Sun - Thu : "+ time1_open.strftime('%I')+":"+time1_open.strftime('%M')+time1_open.strftime('%p')+ ' to ' +time1_close.strftime('%I')+":"+time1_close.strftime('%M')+time1_close.strftime('%p')
                        time2 = "Fri - Sat : "+ time2_open.strftime('%I')+":"+time2_open.strftime('%M')+time2_open.strftime('%p')+ ' to ' +time2_close.strftime('%I')+":"+time2_close.strftime('%M')+time2_close.strftime('%p')
                        item['store_hours'] = time1 + ", " + time2
                    except:
                        pdb.set_trace()
                    item['store_type'] = store['RestType']
                    if item['address']+item['phone_number'] not in self.history:
                        self.history.append(item['address']+item['phone_number'])
                        yield item  
                except:
                    pdb.set_trace()
        except:
            pass

        

    