import scrapy
import json
import datetime

class Peispider(scrapy.Spider):
    name = "peispider"
    item = {}
    def start_requests(self):
        init_url  = 'https://www.peiwei.com/api/location/autocomplete'
        yield scrapy.Request(url=init_url, callback=self.body)   

    def body(self, response):
        fetch_data = json.loads(response.body)
        store_list = fetch_data['Data']
        for store in store_list:
            detail_url = 'https://www.peiwei.com/api/location/stores?id=' + str(store['value']['StoreID'])
            yield scrapy.Request(url=detail_url, callback=self.parse)
    
    def parse(self, response):
        data = json.loads(response.body)
        for store in data['Stores']:
            self.item['store_name'] = store['Shop']
            self.item['store_number'] = ''
            self.item['address'] = store['Address1']
            self.item['address2'] = store['Address2']
            self.item['city'] = store['City']
            self.item['state'] = store['State']
            self.item['zip_code'] = store['Zip']
            self.item['country'] = 'United States'
            self.item['phone_number'] = store['Phone']
            self.item['latitude'] = store['Latitude']
            self.item['longitude'] = store['Longitude']
            time1_close = store['OperatingHours'][0]['ClosingTime'][6:-2]
            time1_close = datetime.datetime.utcfromtimestamp(int(int(time1_close)/1000))
            time1_open = store['OperatingHours'][0]['OpeningTime'][6:-2]
            time1_open = datetime.datetime.utcfromtimestamp(int(int(time1_open)/1000))
            time2_close = store['OperatingHours'][6]['ClosingTime'][6:-2]
            time2_close = datetime.datetime.utcfromtimestamp(int(int(time2_close)/1000))
            time2_open = store['OperatingHours'][6]['OpeningTime'][6:-2]
            time2_open = datetime.datetime.utcfromtimestamp(int(int(time2_open)/1000))
            time1 = "Sun - Thu : "+ time1_open.strftime('%I')+":"+time1_open.strftime('%M')+time1_open.strftime('%p')+ ' to ' +time1_close.strftime('%I')+":"+time1_close.strftime('%M')+time1_close.strftime('%p')
            time2 = "Fri - Sat : "+ time2_open.strftime('%I')+":"+time2_open.strftime('%M')+time2_open.strftime('%p')+ ' to ' +time2_close.strftime('%I')+":"+time2_close.strftime('%M')+time2_close.strftime('%p')
            self.item['store_hours'] = time1 + ", " + time2
            self.item['store_type'] = store['RestType']
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            yield self.item

        

    