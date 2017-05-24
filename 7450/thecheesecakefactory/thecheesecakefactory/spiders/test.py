import scrapy
import os
import json
from lxml import etree

class test(scrapy.Spider):
    name = "test"
    item = {}

    def start_requests(self):
            init_url  = 'https://maps.googleapis.com/maps/api/js/ViewportInfoService.GetViewportInfo?1m6&1m2&1d41.236083984375&2d-80.68386840820312&2m2&1d45.338653564453125&2d-77.4228515625&2u9&4sen-US&5e0&6sm%40378000000&7b0&8e0&callback=_xdc_._tublfk&token=78951'
            yield scrapy.Request(url=init_url, callback=self.parse)  

    def parse(self, response):
        data = (response.body).split('(')[1].strip()[:-2]
        tree = json.loads(data)
        
        # print(data)
        # store_list = tree.xpath('.//response//collection//poi')
        # for store in store_list:
        #     self.item['store_name'] = store.xpath('.//mallname/text()')
        #     self.item['store_number'] = ''
        #     self.item['address'] = store.xpath('.//address1/text()')
        #     self.item['address2'] = store.xpath('.//address2/text()')
        #     self.item['city'] = store.xpath('.//city/text()')
        #     self.item['state'] = store.xpath('.//state/text()')
        #     self.item['zip_code'] = store.xpath('.//postalcode/text()')
        #     self.item['country'] = store.xpath('.//country/text()')
        #     self.item['phone_number'] = store.xpath('.//phone/text()')
        #     self.item['latitude'] = store.xpath('.//latitude/text()')
        #     self.item['longitude'] = store.xpath('.//longitude/text()')
        #     self.item['store_hours'] = ''
        #     try:
        #         self.item['store_hours'] = store.xpath('.//hourslabel1/text()')[0] + ' : ' + str(store.xpath('.//hoursfromto1/text()')[0]) + ', ' + store.xpath('.//hourslabel2/text()')[0] + ' : ' + store.xpath('.//hoursfromto2/text()')[0] + ', ' + store.xpath('.//hourslabel3/text()')[0] + ' : ' + store.xpath('.//hoursfromto3/text()')[0]
        #     except:
        #         pass
        #     self.item['store_type'] = ''
        #     self.item['other_fields'] = ''
        #     self.item['distributor_name'] = ''
        #     yield self.item
        
    
        