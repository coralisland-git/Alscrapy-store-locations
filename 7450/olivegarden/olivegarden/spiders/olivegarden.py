import scrapy
from lxml import etree
import os
import json
import unicodedata

class olivegarden(scrapy.Spider):
    name = "olivegarden"
    item = {}
    history = ['']
    url_template = 'http://www.olivegarden.com/locations/'

    def start_requests(self):
        init_url  = 'http://www.olivegarden.com/locations/location-search-ajax'
        header = {
        'X-Requested-With':'XMLHttpRequest'
        }
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/geolocation.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)

        for location in location_list:
            form_data = {
            'geoCode':str(location['latitude'])+','+str(location['longitude'])
            }
            yield scrapy.FormRequest(url=init_url,
                formdata=form_data, headers=header, callback=self.body)

    def body(self, response):
        tree = etree.HTML(response.body)
        store_list = tree.xpath('.//div[@class="row"]')
        
        for store in store_list:
            try:
                address = store.xpath('.//div[@class="span3 margin_lft_07"]//span[2]/text()')
                state = address[1].split(',')[1].strip().split(' ')[0].strip()
                city = address[1].split(',')[0].strip()
                name = store.xpath('.//div[@class="span3 margin_lft_07"]//span[1]//a/text()')[0].strip()
                link_key = store.xpath('.//span[@class="direct-text-size"]//a[@class="linkcolortxt"]/@id')[0].split('-')[1].strip()
                link_detail = self.url_template + '' + state + '/' + city + '/' + name + '/' + link_key
                yield scrapy.Request(url=link_detail, callback=self.parse)   
            except:
                pass     

    def parse(self, response):
        tree = etree.HTML(response.body)
        self.item['store_name'] = tree.xpath('.//div[@class="left-bar"]//h1[@class="style_h1"]/text()')[0].strip()
        self.item['store_number'] = ''
        address = tree.xpath('.//div[@class="left-bar"]//p[@id="info-link-webhead"]/text()')
        self.item['address'] = address[0].strip()
        self.item['address2'] = ''
        self.item['city'] = address[1].split(',')[0].strip()
        self.item['state'] = address[1].split(',')[1].strip().split(' ')[0].strip()
        self.item['zip_code'] = address[1].split(',')[1].strip().split(' ')[1].strip()
        self.item['country'] = 'United States'
        self.item['phone_number'] = address[2].strip()
        self.item['latitude'] = ''
        self.item['longitude'] = ''
        h_temp = ''
        hour_list = tree.xpath('.//div[@id="restaurant-hours-reload"]//div[@class="day-exp"]')
        for hour in hour_list:
            h_temp = h_temp + hour.xpath('.//ul[@class="inline top-bar"]//li["weekday"]/text()')[0] + ' : ' + hour.xpath('.//ul[@class="inline top-bar"]//li[@class="time"]/text()')[0].strip() + ', '
            h_temp = unicodedata.normalize('NFKD', h_temp).encode('ascii','ignore')
        self.item['store_hours'] = h_temp[:-2]
        self.item['store_type'] = ''
        self.item['other_fields'] = ''
        self.item['distributor_name'] = ''
        if self.item['store_name']+str(self.item['store_number']) not in self.history:
                yield self.item
                self.history.append(self.item['store_name']+str(self.item['store_number']))