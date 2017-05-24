import scrapy
import json
import re
from lxml import etree

class Dipspider(scrapy.Spider):
    name = "dipspider"
    item = {}
    
    def start_requests(self):
        load_url = 'http://www.diptyqueparis.com/store-locator/index/search/'
        yield scrapy.Request(url=load_url , callback=self.mbody)  

    def mbody(self, response):
        fetch_data = json.loads(response.body)
        tree = etree.HTML(fetch_data['html'])
        store_list = tree.xpath('.//div[@class="sidebar-nav"][2]//ul//li//a')

        for store in store_list:
            yield scrapy.Request(url=store.attrib['data-url'], callback=self.parse)
    
    def parse(self, response):
        store_detail = json.loads(response.body)
        tree = etree.HTML(store_detail['html'])
        name = tree.xpath('.//div[@class="s-content"]//h3//text()')
        address = tree.xpath('.//div[@class="s-content"]//div[@class="address"]//p[1]//text()')
        zipcode = (address[1].split(", ")[1]).split(" ")[0]
        zipcode = zipcode.strip()
        temp = (address[1].split(", ")[0]).split(" ")
        state = temp[len(temp)-1]
        re_state = re.compile('(^[A-Z][A-Z])')
        phone = tree.xpath('.//div[@class="s-content"]//div[@class="address"]//p[2]//text()')
        self.item['store_name'] = name
        self.item['store_number'] = ''
        self.item['address'] = address[0]
        self.item['address2'] = ''
        self.item['city'] = (address[1].split(',')[0]).strip()
        self.item['state'] = ''
        self.item['zip_code'] = zipcode
        self.item['country'] = ''
        self.item['phone_number'] = phone[0].strip()
        self.item['latitude'] = ''
        self.item['longitude'] = ''
        self.item['store_hours'] = ''
        self.item['store_type'] = ''
        self.item['other_fields'] = ''
        self.item['distributor_name'] = ''
        if len(state) == 2 and re_state.match(state) and len(zipcode) == 5:
            self.item['state'] = state
            city = (address[1].split(',')[0]).strip()
            self.item['city'] = city[:-2]
            self.item['country'] = 'United States'
            yield self.item