import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
import usaddress

class honeydewdonuts(scrapy.Spider):
    name = 'honeydewdonuts'
    domain = 'http://www.honeydewdonuts.com'
    history = []

    def start_requests(self): 
        init_url = 'http://www.honeydewdonuts.com/locations/'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = response.xpath('//dl[@class="store"]')
        for store in store_list:
            phone = store.xpath('./div[2]/dd//text()').extract_first()
            if not phone or 'Drive Thru' in phone:
                phone = ''
            detail_url = store.xpath('./dt/a//@href').extract_first()
            yield scrapy.FormRequest(url=self.domain + detail_url, callback=self.parse, meta={'phone': phone})             

    def parse(self, response):
        phone = response.meta.get('phone')
        store_list = response.xpath('//section[@id="mainContent"]')
        for store in store_list:
            item = ChainItem()
            item['store_name'] = self.validate(store.xpath('.//h2//text()').extract_first())
            addr_list= store.xpath('.//address//text()').extract()
            address = ''
            for addr in addr_list[:-2]:
                address += addr + ' '
            addr = usaddress.parse(self.validate(address))
            item['address'] = ''
            item['city'] = ''
            item['state'] = ''
            item['zip_code'] = ''
            for temp in addr:
                if temp[1] == 'PlaceName':
                    item['city'] += temp[0].replace(',','') + ' '
                elif temp[1] == 'StateName':
                    item['state'] = temp[0].replace(',','')
                elif temp[1] == 'ZipCode':
                    item['zip_code'] = temp[0].replace(',','')
                else:
                    item['address'] += temp[0].replace(',', '') + ' '
            item['country'] = "United States"
            item['phone_number'] = phone
            yield item          

    def validate(self, item):
        try:
            return item.strip().encode('utf-8').translate(None, '\r\n\t')
        except:
            return ''

    def normalize(self, arr):
        newarr = []
        for item in arr:
            if self.validate(item) is '':
                pass
            else:
                newarr.append(self.validate(item))
        return newarr