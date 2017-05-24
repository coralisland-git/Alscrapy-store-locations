import scrapy
import json
import csv
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

from selenium import webdriver
from lxml import html

class sport(scrapy.Spider):
    name = "sport"
    domain = "https://www.sportclips.com/"
    history = ['']

    def start_requests(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)

        for location in location_list:
            header = {
                'accept':'*/*',
                'accept-encoding':'gzip, deflate, br',
                'content-type':'application/json; charset=UTF-8',
                'origin':'https://www.sportclips.com',
                'referer':'https://www.sportclips.com/store-locator?location='+location['city']+'&radius=100',
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
                'x-requested-with':'XMLHttpRequest',
             }
            data = {'strLocation': location['city'], 'strLat': location['latitude'], 'strLng': location['longitude'], 'strRadius': "100", 'country': 'US'}
            init_url  = 'https://www.sportclips.com/CustomWeb/StoreLocator.asmx/SearchByLocation'
            request = scrapy.Request(url=init_url ,method="POST", body=json.dumps(data), headers=header, callback=self.parse_page) 
            yield request

    def parse_page(self, response):
        data = json.loads(response.body)
        store_list = json.loads(data['d'])['Results']
        for store in store_list:
            try:
                print('============',store['Url'].strip())
                request = scrapy.Request(url=store['Url'].strip(), callback=self.parse_store)
                request.meta['store_name'] = store['Title']
                request.meta['store_number'] = ''
                address = store['Address']
                try:
                    if ', Suite' in address:
                        address = address.replace(', Suite','|Suite') 
                    addr1 = address.split(',')[0].split('|')
                    request.meta['address'] = addr1[0].strip()
                    if len(addr1) == 3:
                        request.meta['address2'] = addr1[1].strip()
                        request.meta['city'] = addr1[2].strip()
                        request.meta['state'] = address.split(',')[1].split('|')[0].strip().split(' ')[0]
                        request.meta['zip_code'] = address.split(',')[1].split('|')[0].strip().split(' ')[1]
                    else :
                        request.meta['address2'] = ''
                        request.meta['city'] = addr1[1].strip()  
                        request.meta['state'] = address.split(',')[1].split('|')[0].strip().split(' ')[0]
                        request.meta['zip_code'] = address.split(',')[1].split('|')[0].strip().split(' ')[1]
                except:
                    request.meta['address'] = '' 
                    request.meta['address2'] = ''                                 
                
                request.meta['country'] = 'United States'
                try:
                    request.meta['phone_number'] = address.split(',')[1].split('|')[2]
                except:
                    request.meta['phone_number'] = ''
                request.meta['latitude'] = str(store['Lat']).strip()
                request.meta['longitude'] = str(store['Long']).strip()
                yield request 
            except:
                pass        

    def parse_store(self, response):
        item = ChainItem()
        data = response.xpath('.//div[@class="home-content"]//div[@class="store-block"]//table[1]//tbody//tr')
        open_hours = ''
        for hours in data:
            open_hours = open_hours + hours.xpath('.//th//text()').extract_first() + hours.xpath('.//td//text()').extract_first() + ', '
        item['store_name'] = response.meta["store_name"]
        item['store_number'] = ""
        item['address'] = response.meta["address"]
        item['phone_number'] = response.meta["phone_number"]
        item['city'] = response.meta["city"]
        item['state'] = response.meta["state"]
        item['zip_code'] = response.meta["zip_code"]
        item['country'] = response.meta["country"]
        item['latitude'] = response.meta['latitude']
        item['longitude'] = response.meta['longitude']
        item['store_hours'] = open_hours[:-2]
        item['store_type'] = ''
        item['other_fields'] = ''
        item['coming_soon'] = '0'
        if item['store_name']+str(item['store_number']) not in self.history:
            yield item
            self.history.append(item['store_name']+str(item['store_number']))

            
    