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
import unicodedata


class CartridgeworldSpider(scrapy.Spider):
    name = 'cartridgeworld3'
    domain = 'https://www.cartridgeworld.com'
    us_state_list = []
    us_location_list = []
    ca_location_list = []
    history = []

    def __init__(self):

        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_States.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        for location in location_list:
            self.us_state_list.append(location['abbreviation'])

        file_path_us = script_dir + '/geo/US_Cities.json'
        with open(file_path_us) as data_file:    
            self.us_location_list = json.load(data_file)

        file_path_ca = script_dir + '/geo/CA_Cities.json'
        with open(file_path_ca) as data_file:    
            self.ca_location_list = json.load(data_file)

    def start_requests(self):
        init_url = 'https://www.cartridgeworld.com/store/search?SearchQuery=%s&SourceLatitude=%s&SourceLongitude=%s'
        for location in self.us_location_list:
            url = init_url % (location['city'].replace(' ', '+'), location['latitude'], location['longitude'])  
            yield scrapy.Request(url=url, callback=self.body)
        
        for location in self.ca_location_list:
            url = init_url % (location['city'].replace(' ', '+'), location['latitude'], location['longitude'])
            yield scrapy.Request(url=url, callback=self.body)

    def body(self, response):
        stores_list = []
        try:
            stores_list = response.xpath('//li[@class="js-store-box"]//div[@class="store-box-inner"]')
        except:
            stores_list = []
        if stores_list:
            for store in stores_list:
                latitude = store.xpath('./input[@class="js-store-latitude"]/@value').extract_first()
                longitude = store.xpath('./input[@class="js-store-longitude"]/@value').extract_first()
                store_name = store.xpath('./a[@class="store-title"]/text()').extract_first()
                phone = store.xpath('./dl/dd/a/text()').extract_first()
                if not phone in self.history:
                    self.history.append(phone)
                    detail_link = self.domain + store.xpath('./a[@class="store-title"]/@href').extract_first()
                    addr_list = store.xpath('.//dl//dd/text()').extract()
                    temp_address = ''
                    for addr in addr_list:
                        temp_address += addr + ' '
                    request = scrapy.Request(url=detail_link, callback=self.body_detail)
                    request.meta['latitude'] = latitude
                    request.meta['longitude'] = longitude
                    request.meta['store_name'] = store_name
                    request.meta['phone'] = phone
                    request.meta['temp_address'] = temp_address
                    yield request
                else:
                    pass
        else:
            pass

    def body_detail(self, response):
        try:
            hour_list = response.xpath('//dl[@class="store-details-hours clearfix"]//dd//p/text()').extract()
            hour_list = self.eliminatespace(hour_list)
            h_temp = ''
            for hour in hour_list:
                if ': ' in hour.strip():
                    h_temp += self.format(hour).strip() + ', '
        except:
            pass
        item = ChainItem()
        item['latitude'] = response.meta['latitude']
        item['longitude'] = response.meta['longitude']
        item['store_name'] = response.meta['store_name']
        item['phone_number'] = response.meta['phone']
        item['store_hours'] = h_temp[:-2]
        if item['store_hours']:
            item['coming_soon'] = '0'
        else:
            item['coming_soon'] = '1'
        temp_address = response.meta['temp_address']
        city = ''
        state = ''
        zip_code = ''
        address = ''
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
        item['country'] = 'United States'
        if not state in self.us_state_list:
            item['country'] = 'Canada'
            temp_list = temp_address.split(' ')
            count = len(temp_list)
            zip_code = temp_list[count - 2] + temp_list[count - 1]
            state = temp_list[count - 3]
            city = temp_list[count - 4]
            i = 0
            while i < count - 4:
                address += temp_list[i].replace(',', '').strip() + ' '
                i += 1
        item['address'] = address
        item['city'] = city
        item['state'] = state
        item['zip_code'] = zip_code
        yield item
        
    def format(self, item):
        try:
            return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
        except:
            return ''

    def eliminatespace(self, items):
        tmp = []
        for item in items:
            if self.validate(item) != '':
                tmp.append(self.validate(item))
        return tmp

    def validate(self, item):
        try:
            return item.strip()
        except:
            pass