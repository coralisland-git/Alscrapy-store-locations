import scrapy
import json

class Penspider(scrapy.Spider):
    name = "penspider"
    item = {}
    
    def start_requests(self):
        init_url  = 'https://www.penhaligons.com/us/page/storelocator/'
        yield scrapy.Request(url=init_url, callback=self.parse)    

    def parse(self, response):
        
        store_data = response.xpath('.//div[@class="store_table"]//script/text()').extract_first()
        data = store_data.split('myStores = ')[1][:-1]
        store_list = json.loads(data)
        
        for store in store_list['stores']:
            self.item['store_name'] = store['name']
            self.item['store_number'] = store['id']
            self.item['address'] = store['address1']
            self.item['address2'] = store['address2']
            self.item['city'] = store['town']
            self.item['state'] = store['postcode'].split(' ')[0]
            self.item['zip_code'] = store['postcode'].split(' ')[1]
            self.item['country'] = store['country']
            self.item['phone_number'] = store['storecontacts']
            self.item['latitude'] = store['pca_wgs84_latitude']
            self.item['longitude'] = store['pca_wgs84_longitude']
            if store['openinghours'] is not None:
                store['openinghours'] = store['openinghours'].strip()
                store['openinghours'] = store['openinghours'].replace('<br />',',')
                store['openinghours'] = store['openinghours'].replace('#','')
            self.item['store_hours'] = store['openinghours']
            self.item['store_type'] = store['storeType']
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            yield self.item