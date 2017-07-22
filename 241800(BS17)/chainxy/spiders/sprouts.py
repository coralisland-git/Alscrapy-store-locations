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

class sprouts(scrapy.Spider):
    name = 'sprouts'
    domain = ''
    history = []

    def start_requests(self):
        init_url  = 'https://www.sprouts.com/stores/search/'
        yield scrapy.Request(url=init_url, callback=self.body)  

    def body(self, response):
        state_list = response.xpath('.//div[@class="sprouts-select-container"]//select//option')
        for state in state_list:
            url  = 'https://www.sprouts.com/stores/search/-/store-search/view?_storesearch_WAR_storelocatorportlet_latitude=&_storesearch_WAR_storelocatorportlet_longitude=&zip=&city=&state='+state.xpath('./@value').extract_first().strip()
            yield scrapy.Request(url=url, callback=self.parse)  

    def parse(self, response):
        try:
            store_list = response.xpath('.//div[@class="store-finder-summary-container store-resultitem"]')
            for store in store_list:
                item = ChainItem()
                item['store_name'] = (store.xpath('.//div[@class="store-finder-store-summary-name"]//h3//a/text()').extract_first()).split('(')[0].strip()
                item['store_number'] = (store.xpath('.//div[@class="store-finder-store-summary-name"]//h3//a/text()').extract_first()).split('(')[1].strip().split('#')[1][:-1].strip()
                addr = store.xpath('.//div[@class="store-finder-summary-address"]/text()').extract()
                item['address'] = addr[0].strip()
                item['address2'] = ''
                item['city'] = addr[1].split(',')[0].strip()
                item['state'] = addr[1].split(',')[1].strip().split(' ')[0].strip()
                item['zip_code'] = addr[1].split(',')[1].strip().split(' ')[1].strip()
                item['country'] = 'United States'
                item['phone_number'] = addr[2].strip()
                try:
                    item['store_hours'] = (store.xpath('.//div[@class="store-finder-store-summary-name"]//p/text()').extract_first()).strip()               
                    item['store_hours'] = (store.xpath('.//div[@class="store-finder-summary-hours"]//strong/text()').extract_first()).strip()
                except:
                    pass
                if item['address']+item['phone_number'] not in self.history:
                    self.history.append(item['address']+item['phone_number'])
                    yield item 
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
