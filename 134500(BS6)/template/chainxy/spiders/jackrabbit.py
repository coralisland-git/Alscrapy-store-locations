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

class JackrabbitSpider(scrapy.Spider):
    name = 'jackrabbit'
    domain = 'https://www.jackrabbit.com'
    request_url = 'https://a.tiles.mapbox.com/v4/chchchawes.pjli078d/features.json?access_token=pk.eyJ1IjoiY2hjaGNoYXdlcyIsImEiOiJjaW1udGN3djEwMDFndmtreTFvYm0waWw0In0.t4gR2FndaeaE1i5bCEUFzA'

    def start_requests(self):
        url = self.request_url
        yield scrapy.Request(url=url, callback=self.body)
    
    def body(self, response):
        if response.body:
            stores_list = json.loads(response.body)
            for store in stores_list['features']:
                item = ChainItem()
                item['latitude'] = store['geometry']['coordinates'][1]
                item['longitude'] = store['geometry']['coordinates'][0]
                item['store_name'] = store['properties']['title']
                item['store_number'] = store['properties']['id']
                description = store['properties']['description']
                zip_code = ''
                city = ''
                state = ''
                address = ''
                description = '<div>' + description + '</div>'
                descript = etree.HTML(description)
                store_info = descript.xpath('//div/text()')
                i = len(store_info)
                item['phone_number'] = store_info[1].strip()
                j = 3
                hour_list = ''
                while j < i:
                    if store_info[j].strip() !='':
                        hour_list += self.validate(store_info[j].strip()) + ', '
                    j += 1
                item['store_hours'] = hour_list[:-2]
                temp_address = store_info[0].strip()
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
                item['zip_code'] = zip_code
                item['city'] = city
                item['state'] = state
                item['address'] = address
                if item['store_hours']:
                    item['coming_soon'] = '0'
                else:
                    item['coming_soon'] = '1'
                item['country'] = 'United States'
                yield item
        else:
            pass

    def validate(self, item):
        try:
            return item.strip().replace('\n', '').replace('\t', '')
        except:
            return ''