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
import pdb

class carquest(scrapy.Spider):
    name = 'carquest'
    domain = 'http://www.carquest.com/'
    history = []
    
    def start_requests(self):
        init_url = 'http://www.carquest.com/stores'
        yield scrapy.Request(url=init_url, callback=self.parse_state) 

    def parse_state(self, response):
        state_list = response.xpath('//a[@class="c-directory-list-content-item-link"]//@href').extract()
        for state in state_list : 
            state_link = self.domain + state
            if len(state.split('/')) == 2:
                yield scrapy.Request(url=state_link, callback=self.parse_city)  
            if len(state.split('/')) == 3:
                yield scrapy.Request(url=state_link, callback=self.parse_store)  
            else :
                yield scrapy.Request(url=state_link, callback=self.parse_page)

    def parse_city(self, response):
        city_list = response.xpath('//a[@class="c-directory-list-content-item-link"]//@href').extract()
        for city in city_list :
            city_link = self.domain + city[3:]
            if len(city.split('/')) == 4:
                yield scrapy.Request(url=city_link, callback=self.parse_store)
            if len(city.split('/')) == 5:
                yield scrapy.Request(url=city_link, callback=self.parse_page)

    def parse_store(self, response):
        store_list = response.xpath('//div[@class="c-location-grid-item-link-wrapper"]//a[contains(@class, "c-location-grid-item-link")][1]//@href').extract()
        for store in store_list:
            store_link = self.domain + store[6:]
            yield scrapy.Request(url=store_link, callback=self.parse_page)

    def parse_page(self, response):
        store = response.xpath('.//div[@class="nap-info-content"]')
        item = ChainItem()
        item['store_name'] = store.xpath('.//span[@class="location-name-brand"]//text()').extract_first()
        item['store_number'] = store.xpath('.//span[@class="location-name-geo"]//text()').extract_first().split('#')[1]
        address = store.xpath('.//address[@class="c-address"]')
        item['address'] = self.validate(address.xpath('.//span[@class="c-address-street"]//text()').extract_first())
        item['city'] = address.xpath('.//span[@itemprop="addressLocality"]//text()').extract_first()
        item['state'] = address.xpath('.//abbr[@itemprop="addressRegion"]//text()').extract_first()
        item['zip_code'] = address.xpath('.//span[@class="c-address-postal-code"]//text()').extract_first()
        item['country'] = "United States"
        item['latitude'] = store.xpath('.//meta[@itemprop="latitude"]//@content').extract_first()
        item['longitude'] = store.xpath('.//meta[@itemprop="longitude"]//@content').extract_first()
        item['phone_number'] = store.xpath('.//span[@id="telephone"]//text()').extract_first()
        h_temp = ''
        hour_list = store.xpath('.//tr[contains(@class, "c-location-hours-details-row")]')
        for hour in hour_list:
            temp = self.eliminate_space(hour.xpath('.//text()').extract())
            for te in temp:
                h_temp += te + ' '
            h_temp += ', '
        item['store_hours'] = h_temp[:-2]
        yield item          

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
