import scrapy, time
import json
import requests
import os

class Zaraspider(scrapy.Spider):
    name = 'zaraspider'
    item = {}
    history = ['']
    def start_requests(self):

        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language':'en-US,en;q=0.8',
            'Connection':'keep-alive',
            'content-type': 'application/json',
            'Host': 'www.zara.com',
            # 'Referer': 'https://www.zara.com/ca/en/stores-c11108.html',
            'Upgrade-Insecure-Requests':1,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest'
            }

        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/cities.json'
        with open(file_path) as data_file:    
            data = json.load(data_file)
        
        for location in data:
        
            # params = {'sensor': 'false', 'address': state['city']}
            # # print("=============",state['city'])
            # r = requests.get(map_url, params=params)
            # results = r.json()['results']
            # location = results[0]['geometry']['location']   
            url = 'https://www.zara.com/ca/en/stores-locator/search?lat='+str(location["latitude"])+'&lng='+str(location["longitude"])+'&isGlobalSearch=true&ajax=true'
            yield scrapy.Request(url=url, method="GET", headers=header, callback=self.parse)    

    def parse(self, response):
        fetch_data = json.loads(response.body)
        for store in fetch_data:
        
            self.item['store_name'] = store['name']
            self.item['store_number'] = store['id']
            s_address = ''
            for address in store['addressLines']:
                s_address = s_address + address + ', '
            self.item['address'] = s_address[:-2]
            self.item['address2'] = ''
            self.item['city'] = store['city']
            self.item['state'] = store['state']
            self.item['zip_code'] = store['zipCode']
            self.item['country'] = store['country']
            s_phone = ''
            for phone in store['phones']:
                s_phone = s_phone + phone + ', '
            self.item['phone_number'] = s_phone[:-2]
            self.item['latitude'] = store['latitude']
            self.item['longitude'] = store['longitude']
            s_openingHours = ''
            for hours in store['openingHours']:
                s_hours = str(hours['date']) + " : "
                for cotime in hours['openingHoursInterval']:
                    s_hours = s_hours + str(cotime['openTime']) + '-'+ str(cotime['closeTime']) + ' '
                s_openingHours = s_openingHours + s_hours + ", "
            self.item['store_hours'] = s_openingHours[:-2]
            self.item['store_type'] = store['type']
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            if self.item['store_number'] not in self.history:
                yield self.item
            self.history.append(store['id'])
    
