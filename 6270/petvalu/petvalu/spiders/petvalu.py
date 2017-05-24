import scrapy
from lxml import etree
import os
import json

class petvalu(scrapy.Spider):
    name = "petvalu"
    item = {}
    history = ['']
    def start_requests(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        for location in location_list:
            init_url  = 'http://us.petvalu.com/location?ajax=1&city_search='+location['city']+'&province=&limit=undefined&adoption=false&grooming=false&raw_food=false&dog_wash=false&small_pets=false'
            yield scrapy.Request(url=init_url, callback=self.parse)   
    
    def parse(self, response):
        
        data = response.xpath('.//div[@class="fl w100"]//li')
        for store in data:
            try:
                self.item['store_name'] = (store.xpath('.//div[@class="text"]//h1/text()').extract_first()).strip()
                self.item['store_number'] = ''
                address = store.xpath('.//div[@class="text"]//p[1]/text()').extract()
                self.item['address'] = address[0].strip()
                self.item['address2'] = ''
                cnt = 2
                if len(address) == 3:
                    self.item['address2'] = address[2].strip()
                    cnt = 3
                self.item['city'] = address[cnt].strip().split(',')[0].strip()
                self.item['state'] = address[cnt].strip().split(',')[1].strip().split(' ')[0].strip()
                self.item['zip_code'] = address[cnt].strip().split(',')[1].strip().split(' ')[1].strip()
                self.item['country'] = 'United States'
                self.item['phone_number'] = (store.xpath('.//div[@class="text"]//p[2]/text()').extract_first()).split(':')[1].strip()
                self.item['latitude'] = ''
                self.item['longitude'] = ''
                h_temp = ''
                hours = store.xpath('.//div[@class="hours"]//p')
                for hour in hours:
                    h_temp = h_temp + (hour.xpath('./text()').extract_first()).strip() + ' '
                self.item['store_hours'] = h_temp
                self.item['store_type'] = ''
                self.item['other_fields'] = ''
                self.item['distributor_name'] = ''
                if self.item['zip_code'] not in self.history:
                    yield self.item
                self.history.append(self.item['zip_code'])
            except:
                pass


