import scrapy, time
import selenium
from selenium import webdriver
from lxml import etree
import os
import json

class Saksspider(scrapy.Spider):
    name = "saksspider"
    item = {}    

    def start_requests(self):
        init_url  = 'http://www.saksfifthavenue.com'
        header = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'en-US,en;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.saksfifthavenue.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        yield scrapy.Request(url=init_url, method='GET', headers=header, callback=self.parse)    
        
    def parse(self,response):       

        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        # for location in location_list:
        self.driver = webdriver.Chrome("./chromedriver") 
        self.driver.get("http://www.saksfifthavenue.com/stores/stores.jsp")  
        # self.driver.find_element_by_id("close-button").click()
        city = self.driver.find_element_by_id("storesCity")
        state = self.driver.find_element_by_id("storesState_input")
        city.send_keys("Los Angeles")
        state.send_keys("California")
        self.driver.find_element_by_id("btnSearchStores").click()
        source = self.driver.page_source.encode("utf8")
        with open('res6.html', 'wb') as f:
            f.write(source)
        # self.driver.close()
        tree = etree.HTML(source)
        # store_list = tree.xpath('//li[@class="store-list-item vcard address"]')
        # for store in store_list:
        #     self.item['store_name'] = store.xpath('.//h3/text()')[0].strip()
        #     self.item['store_number'] = ''
        #     self.item['address'] = store.xpath('.//div[@class="adr"]//span[@class="street-address"]/text()')[0].strip()
        #     self.item['address2'] = ''
        #     self.item['city'] = store.xpath('.//div[@class="adr"]//span[@class="locality"]/text()')[0].strip()
        #     self.item['state'] = store.xpath('.//div[@class="adr"]//abbr[@class="region"]/text()')[0].strip()
        #     self.item['zip_code'] = store.xpath('.//div[@class="adr"]//span[@class="postal-code"]/text()')[0].strip()
        #     self.item['country'] = 'United States'
        #     self.item['phone_number'] = store.xpath('.//div[@class="tel"]/text()')[0].strip()
        #     self.item['latitude'] = ''
        #     self.item['longitude'] = ''
        #     self.item['store_hours'] = store.xpath('.//time/text()')[0].strip()
        #     self.item['store_type'] = ''
        #     self.item['other_fields'] = ''
        #     self.item['distributor_name'] = ''
        #     yield self.item