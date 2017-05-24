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
import pdb


class Vippetcare(scrapy.Spider):
    name = 'vippetcare'
    domain = 'http://www.vippetcare.com'
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_Cities.json'
        
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self):
        city_list = ["Saint John's",
                    "All Saints",
                    "Liberta",
                    "Potter's" "Village",
                    "Bolans",
                    "Swetes",
                    "Seaview Farm",
                    "Pigotts",
                    "Codrington",
                    "Parham"]


        for location in city_list:
            init_url = 'https://www.vippetcare.com/find-a-clinic/' + location  
            formdata = {
                'vip_location': location,
                'vip_distance': '500',
            }
            headers = {
                'Content-Type' : 'application/x-www-form-urlencoded'
            }
            yield scrapy.FormRequest(url=init_url, method="POST", headers=headers, formdata=formdata, callback=self.body)

    def body(self, response):
        print('~~~~~~~~~~~~~ checking ...............')
        store_list = response.xpath('//tr[@class="vip-locator-result"]')
        for store in store_list:
            try:
                item = ChainItem()
                item['store_name'] = self.validate(store.xpath('.//h4//text()').extract_first())           
                address = self.validate(store.xpath('.//td[@class="loc-list-table-col2"]//p//text()').extract_first())          
                item['address'] = self.validate(address.split(',')[0].split('.')[0])
                try:
                    item['city'] = self.validate(address.split(',')[0].split('.')[1])
                except:
                    item['city'] = self.validate(address.split(',')[0].split(' ')[-1])
                    item['address'] = self.validate(item['address'].replace(item['city'], '')[:-1])
                item['state'] = self.validate(address.split(',')[1]).split(' ')[0]
                item['zip_code'] = self.validate(address.split(',')[1]).split(' ')[1]
                item['country'] = 'United States'
                hour_list = store.xpath('.//ul[@class="vip-time"]//li//text()').extract()
                h_temp = ''
                for hour in hour_list:
                    try:
                        if ('Every' not in hour.split(',')[0]):
                            h_temp += self.validate(hour.split(',')[0].split(' ')[0]) + ' '
                        else:
                            h_temp += self.validate(hour.split(',')[0].split(' ')[1]) + ' '
                        h_temp += self.validate(hour.split('from')[1].split('until')[0]) + '-'
                        h_temp += self.validate(hour.split('from')[1].split('until')[1]) + ', '
                    except:
                        pass
                item['store_hours'] = h_temp[:-2]
                if item['store_name'] in self.history:
                    continue
                self.history.append(item['store_name'])
                yield item
            except:
                pdb.set_trace()  

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''