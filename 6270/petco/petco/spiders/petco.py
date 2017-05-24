import scrapy
from lxml import etree
import os
import json

class petco(scrapy.Spider):
    name = "petco"
    item = {}
    history = ['']

    def start_requests(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        for location in location_list:
            init_url  = 'https://maps.petco.com/api/getAsyncLocations?template=searchResultsMap&level=search&radius=20&search='+location['city']+'%2C+'+location['state']+'%2C+US'
            yield scrapy.Request(url=init_url, callback=self.body)   
    
    def body(self, response):
        data = json.loads(response.body)
        for store in data['markers']:
            detail = etree.HTML(store['info'])
            data_url = detail.xpath('.//div[@class="tlsmap_popup"]//div[@class="rio-popupItem"]//div[@class="rio-popup-locName"]//a/@href')[0]
            self.latitude = str(store['lat'])
            self.longitude = str(store['lng'])
            yield scrapy.Request(url=data_url, callback=self.parse) 
            
    def parse(self, response):
        try :
            detail = response.xpath('.//div[@class="rio-col"][2]')
            self.item['store_name'] = detail.xpath('.//div[@id="rio-locNameWrapper"]//div[@id="rio-locName"]/text()').extract_first().strip()
            self.item['store_number'] = detail.xpath('.//div[@id="rio-locNameWrapper"]//div[@id="rio-storeNum"]/text()').extract_first().strip().split(':')[1].strip()
            self.item['address'] = detail.xpath('.//div[@id="rio-addrWrapper"]//div[@class="rio-addrText"]//span[1]/text()').extract_first().strip()
            self.item['address2'] = ''
            self.item['city'] = detail.xpath('.//div[@id="rio-addrWrapper"]//div[@class="rio-addrText"]//span[2]/text()').extract_first().strip()
            self.item['state'] = detail.xpath('.//div[@id="rio-addrWrapper"]//div[@class="rio-addrText"]//span[3]/text()').extract_first().strip()
            self.item['zip_code'] = detail.xpath('.//div[@id="rio-addrWrapper"]//div[@class="rio-addrText"]//span[4]/text()').extract_first().strip()
            self.item['country'] = 'United States' 
            self.item['phone_number'] = detail.xpath('.//div[@id="rio-phoneWrapper"]//span[@class="rio-phoneText"]/text()').extract_first().strip()
            self.item['latitude'] = self.latitude
            self.item['longitude'] = self.longitude
            h_temp = ''
            hour_list = detail.xpath('.//div[@class="hours"]//div[@class="day-hour-row"]')
            for hour in hour_list:
                h_temp = h_temp + hour.xpath('.//span[@class="daypart"]/text()').extract_first().strip() + ' : ' + hour.xpath('.//span[@class="time"]/text()').extract_first().strip() + ', '
            self.item['store_hours'] = h_temp[:-2]            
            self.item['store_type'] = ''
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            if self.item['store_name']+str(self.item['store_number']) not in self.history:
                yield self.item
                self.history.append(self.item['store_name']+str(self.item['store_number']))
        except:
            pass