import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem

class Buchheitonline(scrapy.Spider):
    name = 'buchheitonline'
    domain = 'http://www.buchheitonline.com'
    history = []

    def start_requests(self):
        init_url = 'http://www.buchheitonline.com/locations.aspx'
        yield scrapy.Request(url=init_url, callback=self.body)

    def body(self, response):
        store_list = response.xpath('//table//table//table//table//tbody//tr//td')
        for store in store_list:
            address = store.xpath('.//text()').extract()
            address = self.normalize(address)
            item = ChainItem()
            item['store_name'] = self.validate(address[0])           
            item['address'] = self.validate(address[1])
            item['city'] = self.validate(address[2].split(',')[0])
            item['state'] = self.validate(address[2].split(',')[1].strip()).split(' ')[0]
            item['zip_code'] = self.validate(address[2].split(',')[1].strip()).split(' ')[1]
            item['phone_number'] = self.validate(address[3])
            item['country'] = 'United States'
            hour_list = self.normalize(address[5:])
            h_temp = ''
            for hour in hour_list:
                if self.validate(hour) is '':
                    pass
                else:
                    h_temp += self.validate(hour).replace("to", "-") + ", "
            item['store_hours'] = h_temp[:-2]
            if item['store_name'] in self.history:
                continue
            self.history.append(item['store_name'])
            yield item

        item = ChainItem()
        address = response.xpath('//table//table//table//tbody//tr//td//span[1]')[0].xpath(".//text()").extract()
        address = self.normalize(address)
        item['store_name'] = self.validate(address[0])
        item['address'] = self.validate(address[1])
        item['city'] = self.validate(address[2].split(',')[0])
        item['state'] = self.validate(address[2].split(',')[1].strip()).split(' ')[0]
        item['zip_code'] = self.validate(address[2].split(',')[1].strip()).split(' ')[1]
        item['phone_number'] = self.validate(address[3])
        item['country'] = 'United States'
        item['store_hours'] = self.validate(address[5].replace("to", "-"))
        yield item

    def validate(self, item):
        try:
            return item.strip().encode('utf-8').translate(None, "\r\n\t").replace("\xc2\xa0", " ")
        except:
            return ''

    def normalize(self, arr):
        newarr = []
        for item in arr:
            if self.validate(item) is '':
                pass
            else:
                newarr.append(item)
        count = 0 
        for item in newarr:
            if 'Hour' in item:
                break
            count += 1 
        if count == 5:
            newarr.pop(2)
        return newarr