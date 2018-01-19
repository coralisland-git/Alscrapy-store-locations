import scrapy
import time
import json

class Alspider(scrapy.Spider):
    name = "alspider"
    item = {}
    url_template = 'https://usa.loccitane.com/tools/datafeeds/StoresJSON.aspx?country='
    def start_requests(self):
        init_url  = 'https://usa.loccitane.com/boutique-locator,82,1,34279,268123.htm'
        yield scrapy.Request(url=init_url, callback=self.mbody)    

    def mbody(self, response):
        options = response.xpath('.//div[@class="countryChoice"]//div[@class="stor_drop"]//div[@class="stor_select"]//select//option/text()').extract()
        for option in options:
            if ' ' in option:
                option = option.replace(' ', '%20')
            url = self.url_template + option
            yield scrapy.Request(url=url, callback=self.parse)  

    def parse(self, response):
        fetch_data = json.loads(response.body)
        store_list = fetch_data['storeList']['store']

        for store in store_list : 
            self.item['store_name'] = store['Name']
            self.item['store_number'] = store['storeID']
            self.item['address'] = store['Address1']
            self.item['address2'] = store['Address2']
            self.item['city'] = store['City']
            self.item['state'] = store['State']
            self.item['zip_code'] = store['ZipCode']
            self.item['country'] = store['Country']
            self.item['phone_number'] = store['Phone']
            self.item['latitude'] = store['coord']['latitude']
            self.item['longitude'] = store['coord']['longitude']
            if store['OpeningHours1'] is not None:
                store['OpeningHours1'] = store['OpeningHours1'].replace('<br/>',',')
            self.item['store_hours'] = store['OpeningHours1']
            self.item['store_type'] = store['Type']
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            yield self.item

        

    
