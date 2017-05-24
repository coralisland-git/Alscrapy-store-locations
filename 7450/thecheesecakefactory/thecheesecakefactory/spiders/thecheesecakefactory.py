import scrapy
import os
import json
from lxml import etree

class cheesecake(scrapy.Spider):
    name = "cheesecake"
    item = {}
    history = ['']

    def start_requests(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        
        for location in location_list:
            init_url  = 'https://hosted.where2getit.com/ajax?lang=fr_FR&xml_request=%3Crequest%3E%3Cappkey%3E18D36CFE-4EA9-11E6-8D1F-49249CAB76FA%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E'+location['city']+'%3C%2Faddressline%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3Ccountry%3EUS%3C%2Fcountry%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E50%7C100%7C150%7C300%7C500%7C750%7C1000%3C%2Fsearchradius%3E%3Cwhere%3E%3Cor%3E%3Ccateringflag%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcateringflag%3E%3Ccurbsideflag%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fcurbsideflag%3E%3Cdeliveryflag%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fdeliveryflag%3E%3Cdoordashflag%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fdoordashflag%3E%3Cbanquets%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fbanquets%3E%3Cpatio%3E%3Ceq%3E%3C%2Feq%3E%3C%2Fpatio%3E%3C%2For%3E%3C%2Fwhere%3E%3Cnobf%3E1%3C%2Fnobf%3E%3Cstateonly%3E1%3C%2Fstateonly%3E%3C%2Fformdata%3E%3C%2Frequest%3E'
                    
            yield scrapy.Request(url=init_url, callback=self.parse)  

    def parse(self, response):
        tree = etree.HTML(response.body)
        store_list = tree.xpath('.//response//collection//poi')
        for store in store_list:
            try:
                self.item['store_name'] = store.xpath('.//mallname/text()')[0]
                self.item['store_number'] = ''
                self.item['address'] = store.xpath('.//address1/text()')
                self.item['address2'] = store.xpath('.//address2/text()')
                self.item['city'] = store.xpath('.//city/text()')
                self.item['state'] = store.xpath('.//state/text()')
                self.item['zip_code'] = store.xpath('.//postalcode/text()')
                self.item['country'] = store.xpath('.//country/text()')
                self.item['phone_number'] = store.xpath('.//phone/text()')[0]
                self.item['latitude'] = store.xpath('.//latitude/text()')
                self.item['longitude'] = store.xpath('.//longitude/text()')
                self.item['store_hours'] = ''
                try:
                    self.item['store_hours'] = store.xpath('.//hourslabel1/text()')[0] + ' : ' + str(store.xpath('.//hoursfromto1/text()')[0]) + ', ' + store.xpath('.//hourslabel2/text()')[0] + ' : ' + store.xpath('.//hoursfromto2/text()')[0] + ', ' + store.xpath('.//hourslabel3/text()')[0] + ' : ' + store.xpath('.//hoursfromto3/text()')[0]
                except:
                    pass
                self.item['store_type'] = ''
                self.item['other_fields'] = ''
                self.item['distributor_name'] = ''
                if self.item['store_name']+str(self.item['store_number']) not in self.history:
                    yield self.item
                    self.history.append(self.item['store_name']+str(self.item['store_number']))
            except:
                pass                    
        
    
        