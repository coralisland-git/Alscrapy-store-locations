import scrapy
from lxml import etree

class Dicksspider(scrapy.Spider):
    name = 'dicksspider'
    item = {}
    history = ['']
    url_template1 = 'https://storelocator.dickssportinggoods.com/responsive/ajax?&xml_request=%3Crequest%3E%3Cappkey%3E17E8F19C-098E-11E7-AC2C-11ACF3F4F7A7%3C%2Fappkey%3E%3Cformdata+id%3D%22locatorsearch%22%3E%3Cdataview%3Estore_default%3C%2Fdataview%3E%3Climit%3E10%3C%2Flimit%3E%3Catleast%3E10%3C%2Fatleast%3E%3Cgeolocs%3E%3Cgeoloc%3E%3Caddressline%3E'
    url_template2 = '%3C%2Faddressline%3E%3Ccountry%3E%3C%2Fcountry%3E%3Clongitude%3E%3C%2Flongitude%3E%3Clatitude%3E%3C%2Flatitude%3E%3C%2Fgeoloc%3E%3C%2Fgeolocs%3E%3Csearchradius%3E25%7C50%7C100%7C250%7C500%7C1000%3C%2Fsearchradius%3E%3Cwhere%3E%3Cbrandname%3E%3Ceq%3EDicks+Sporting+Goods%3C%2Feq%3E%3C%2Fbrandname%3E%3C%2Fwhere%3E%3C%2Fformdata%3E%3C%2Frequest%3E'
    def start_requests(self):
        state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
        for state in state_list: 
            url = self.url_template1 + state + self.url_template2
            yield scrapy.Request(url=url, callback=self.parse)    

    def parse(self, response):
        
        tree = etree.HTML(response.body)
        store_list = tree.xpath('.//response//collection//poi')
        for store in store_list:
            self.item['store_name'] = store.xpath('.//name/text()')
            self.item['store_number'] = ''
            self.item['address'] = store.xpath('.//address1/text()')
            self.item['address2'] = store.xpath('.//address2/text()')
            self.item['city'] = store.xpath('.//city/text()')
            self.item['state'] = store.xpath('.//state/text()')
            self.item['zip_code'] = store.xpath('.//postalcode/text()')
            self.item['country'] = store.xpath('.//country/text()')
            self.item['phone_number'] = store.xpath('.//phone/text()')
            self.item['latitude'] = store.xpath('.//latitude/text()')
            self.item['longitude'] = store.xpath('.//longitude/text()')
            self.item['store_hours'] = store.xpath('.//specialhours/text()')
            self.item['store_type'] = ''
            self.item['other_fields'] = ''
            self.item['distributor_name'] = ''
            yield self.item
        
