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

class unionbank(scrapy.Spider):
    name = 'unionbank'
    domain = 'https://blw.unionbank.com'
    history = []
    count = 1

    def start_requests(self):
        init_url = 'https://blw.unionbank.com/blw/branches/All-State-Branch-Page'
        yield scrapy.Request(url=init_url, callback=self.parse_state) 

    def parse_state(self, response):
        state_list = self.eliminate_space(response.xpath('//div[@class="all-locations-stateOrCity-name"]//a/@href').extract())
        for state in state_list:
            state = self.domain + self.validate(state.split(';')[0])
            yield scrapy.Request(url=state, callback=self.parse_pagenation)

    def parse_pagenation(self, response):
        pagenation_list = response.xpath('//div[@id="pagination-container"]//a[@class="page-number"]/@href').extract()
        if pagenation_list:
            for cnt in range(1, len(pagenation_list)+1):
                pagenation = 'https://blw.unionbank.com/blw/branches/California-%s/State-Level-Branch-Page' %str(cnt)
                yield scrapy.Request(url=pagenation, callback=self.parse_city)
        else :
            yield scrapy.Request(url=response.url, callback=self.parse_city)

    def parse_city(self, response):
        city_list = response.xpath('//div[@id="city-list"]//a/@href').extract()
        for city in city_list:
            city = self.domain + self.validate(city.split(';')[0])
            yield scrapy.Request(url=city, callback=self.parse_store)

    def parse_store(self, response):
        store_list = response.xpath('//div[@id="branchDetails"]//ul')
        for store in store_list:
            try:
                detail = store.xpath('.//li')
                item = ChainItem()
                item['store_name'] = self.validate(detail[1].xpath('./text()').extract_first())
                address = self.validate(detail[0].xpath('./text()').extract_first())
                item['address'] = ''
                item['city'] = ''
                addr = usaddress.parse(address)
                for temp in addr:
                    if temp[1] == 'PlaceName':
                        item['city'] += temp[0].replace(',','') + ' '
                    elif temp[1] == 'StateName':
                        item['state'] = temp[0].replace(',','')
                    elif temp[1] == 'ZipCode':
                        item['zip_code'] = temp[0].replace(',','')
                    else:
                        item['address'] += temp[0].replace(',', '') + ' '
                item['country'] = 'United States'
                item['phone_number'] = self.validate(detail[6].xpath('./text()').extract_first())
                h_temp = ''
                hour_list_title = self.eliminate_space(detail[9].xpath('.//table//td[1]//text()').extract())
                hour_list_time = self.eliminate_space(detail[9].xpath('.//table//td[3]//text()').extract())
                for cnt in range(0, len(hour_list_title)):
                    h_temp += hour_list_title[cnt] + ' ' +hour_list_time[cnt] + ', '
                item['store_hours'] = h_temp[:-2]
                yield item         
            except:
                pdb.set_trace()
                
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