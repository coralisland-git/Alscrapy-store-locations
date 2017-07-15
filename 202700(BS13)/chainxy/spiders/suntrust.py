from __future__ import unicode_literals
import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
import usaddress

class suntrust(scrapy.Spider):
    name = 'suntrust'
    domain = 'http://www.suntrust.com/locations/'
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_Cities.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)
        file_path = script_dir + '/geo/US_States.json'
        with open(file_path) as data_file:    
            self.US_States_list = json.load(data_file)

    def start_requests(self):
        for location in self.location_list:
            init_url = 'https://www.suntrust.com/FindUs/SearchLocations'
            formdata = {
                'Type':'1',
                'Location':(location['city'] + ', ' + self.get_state(location['state'])),
                'EnableLocateMe':'False',
                'Radius':'200',
                'page':'1',
                'currentPage':'1',
                'isAjax':'true',
                'pageSize':'200',
                'isAjax':'true '
            }
            headers = {
                "Accept":"*/*",
                "Accept-Encoding":"gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            yield scrapy.FormRequest(url=init_url, method="POST", headers=headers, formdata=formdata, callback=self.body)

    def body(self, response):
        store_list = response.xpath('//li[@class="suntrust-branch-location-list-item"]')
        if store_list:
            for store in store_list:
                item = ChainItem()
                item['store_name'] = self.validate(store.xpath('.//span[@itemprop="name"]//text()').extract_first())
                item['address'] = self.validate(store.xpath('.//span[@itemprop="streetAddress"]//text()').extract_first())
                item['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]//text()').extract_first())
                item['state'] = self.validate(store.xpath('.//span[@itemprop="addressRegion"]//text()').extract_first())
                item['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]//text()').extract_first())
                item['country'] = 'United States'
                item['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]//text()').extract_first())
                h_temp = ''
                hour_list = store.xpath('.//span[@itemprop="openingHoursSpecification"]//text()').extract()
                for hour in hour_list[1:]:
                    h_temp += self.validate(hour.replace(u'Weekend', '')) + ', '
                item['store_hours'] = h_temp[:-2]
                if item['store_name']+item['phone_number'] not in self.history:
                    self.history.append(item['store_name']+item['phone_number'])
                    yield item

    def validate(self, item):
        try:
            return item.strip().replace(';','')
        except:
            return ''

    def get_state(self, item):
        for state in self.US_States_list:
            if item.lower() in state['name'].lower():
                return state['abbreviation']
        return ''