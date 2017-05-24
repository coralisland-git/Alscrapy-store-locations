import scrapy
from lxml import etree
import os
import json

class moes(scrapy.Spider):
    name = "moes"
    item = {}
    history = ['']

    def start_requests(self):
        init_url  = 'https://www.moes.com/find-a-moes/'
        header = {
        'X-Requested-With':'XMLHttpRequest'
        }
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        for location in location_list:
            form_data = {
            'search[search]':location['city'],
            'search[geo_lat]':str(location['latitude']),
            'search[geo_long]':str(location['longitude'])
            }
            yield scrapy.FormRequest(url='https://www.moes.com/find-a-moes/',
                formdata=form_data, headers=header, callback=self.parse)
    
    def parse(self, response):
        tree = etree.HTML(response.body)
        store_list = tree.xpath('.//div[@class="each-search-location"]')
        for store in store_list:
            try:
                self.item['store_name'] = store.xpath('.//div[1]//div//div[2]//h2//a//h2/text()')[0].strip()
                self.item['store_number'] = ''
                address = store.xpath('.//div[2]//div[2]//div//p[1]/text()')
                self.item['address'] = address[0].strip()
                self.item['address2'] = ''
                self.item['city'] = address[1].split(',')[0].strip()
                self.item['state'] = address[1].split(',')[1].strip().split(' ')[0].strip()
                self.item['zip_code'] = address[1].split(',')[1].strip().split(' ')[1].strip()
                self.item['country'] = 'United States'
                self.item['phone_number'] = store.xpath('.//div[2]//div[2]//div//p[2]//a/text()')[0].strip()
                self.item['latitude'] = ''
                self.item['longitude'] = ''
                h_temp = ''
                for hour in store.xpath('.//div[3]//div[1]//p'):
                    h_temp = h_temp + hour.xpath('./text()')[0].strip() + ', '
                self.item['store_hours'] = h_temp[:-2]
                self.item['store_type'] = ''
                self.item['other_fields'] = ''
                self.item['distributor_name'] = ''
                if self.item['zip_code'] not in self.history:
                    yield self.item
                    self.history.append(self.item['zip_code'])
            except:
                pass                

