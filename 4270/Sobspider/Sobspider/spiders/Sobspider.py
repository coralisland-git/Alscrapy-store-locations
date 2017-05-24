import scrapy
import json

class Sobspider(scrapy.Spider):
    name = "sobspider"
    item = {}
    def start_requests(self):
        init_url  = 'http://www.sobeys.com/en/stores/?lat=50.5099429&lng=-116.0319865&init=1'
        yield scrapy.Request(url=init_url, callback=self.parse)    
    def parse(self, response):
        store_list = json.loads(response.body)
        for store in store_list:
            self.item['store_name'] = store['name'].replace('&amp; ','&')
            self.item['store_number'] = store['store_number']
            self.item['address'] = store['address_1'].replace('&amp; ','&')
            self.item['address2'] = store['address_2']
            self.item['city'] = store['city']
            self.item['state'] = ''
            self.item['zip_code'] = ''
            self.item['country'] = 'United States'
            self.item['phone_number'] = store['phone'] 
            if len(store['phone2']) != 0:
                self.item['phone_number'] = store['phone'] + " , " +store['phone2']
            self.item['latitude'] = store['lat']
            self.item['longitude'] = store['lng']
            h_temp = ''
            for hour in store['hours']:
                h_temp = h_temp + hour['day'] + ' ' + hour['hours'] + ', '
            self.item['store_hours'] = h_temp[:-2]
            self.item['store_type'] = ''
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            yield self.item

        

    