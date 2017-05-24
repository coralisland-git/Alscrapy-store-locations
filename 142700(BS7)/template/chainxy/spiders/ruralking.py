import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html

class ruralking(scrapy.Spider):
    name = 'ruralking'
    domain = 'https://www.ruralking.com'
    history = []

    def start_requests(self):
        init_url = 'https://www.ruralking.com/storelocator/index/loadstore'
        header = {
           ' Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch, br',
           ' Content-type':'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With':'XMLHttpRequest'
        }
        formdata = {
            'address': '',
            'type': 'map'
        }
        yield FormRequest(url=init_url, headers=header, method='POST', callback=self.body, formdata=formdata)

    def body(self, response):
        store_temp = etree.HTML(response.body)
        try:
            store_list = store_temp.xpath('//li[@class="item"]')
            for store in store_list:
                item = ChainItem()
                detail = store.xpath('.//div[@class="info"]//p/text()')
                item['store_name'] = self.validateStoreName(detail[0]).split('#')[0].strip()
                item['store_number'] = self.stringToStoreNumber(item['store_name'])
                addr = self.validate(detail[1])
                item['address'] = self.stringToaddress(addr)[0]
                item['city'] = self.stringToaddress(addr)[1]
                item['state'] = self.stringToaddress(addr)[2]
                temp_string = self.validate(detail[2])
                item['country'] = self.stringToaddress(temp_string)[0]
                item['zip_code'] = self.stringToaddress(temp_string)[1]
                item['phone_number'] = self.validate(detail[3])
                item['store_hours'] = self.validate(detail[4])
                yield item
        except:
            pass

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''
    
    def validateStoreName(self, item):
        try:
            item = item.replace('- NOW OPEN', '').strip()
            return item
        except:
            return item
    
    def stringToStoreNumber(self, item):
        try:
            item_list = item.split('#')
            return item_list[1].strip()
        except:
            return ['none', 'none']
    
    def stringToaddress(self, item):
        try:
            if item.find(',') != -1:
                item_list = item.split(',')
            else:
                item_list = item.split(' ')
            count = len(item_list)
            i = 0
            while i < count:
                item_list[i] = item_list[i].strip()
                i += 1
            return item_list
        except:
            return ['none', 'none', 'none']