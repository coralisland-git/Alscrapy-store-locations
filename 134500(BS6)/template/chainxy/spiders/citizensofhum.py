import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html
import usaddress

class CitizensofhumSpider(scrapy.Spider):
    name = 'citizensofhum'
    domain = 'https://www.citizensofhumanity.com'
    request_url = 'https://www.citizensofhumanity.com/stores'

    def start_requests(self):
        url = self.request_url
        yield scrapy.Request(url=url, callback=self.body)

    def body(self, response):
        data = response.body.split('initial_locations:')[1].split('min_zoom:')[0].strip()[:-1]
        store_list = json.loads(data)
        for store in store_list:
            item = ChainItem()
            item['store_number'] = store['location_id']
            item['store_name'] = store['title']
            item['latitude'] = store['latitude']
            item['longitude'] = store['longitude']
            item['phone_number'] = store['phone']
            city = ''
            address = ''
            state = ''
            zip_code = ''
            temp_address = store['address']
            addr = usaddress.parse(temp_address)
            for temp in addr:
                if temp[1] == 'PlaceName':
                    city += temp[0].replace(',','')	+ ' '
                elif temp[1] == 'StateName':
                    state = temp[0].replace(',','')
                elif temp[1] == 'ZipCode':
                    zip_code = temp[0].replace(',','')
                else:
                    address += temp[0].replace(',','') + ' '
            item['address'] = address
            item['city'] = city
            item['state'] = state
            item['zip_code'] = zip_code
            item['country'] = store['country']
            yield item
        