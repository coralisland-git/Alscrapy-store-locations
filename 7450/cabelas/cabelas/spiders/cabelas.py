import scrapy, time
import selenium
from selenium import webdriver
from lxml import etree
import os
import json

class cabelas(scrapy.Spider):
    name = "cabelas"
    item = {}

    def __init__(self):
        # self.driver = webdriver.Chrome("./chromedriver")
        self.index = 0

    def start_requests(self):
        
        script_dir = os.path.dirname(__file__)
        # file_path = script_dir + '/geo/cities.json'
        # with open(file_path) as data_file:    
        # #     location_list = json.load(data_file)
        # self.driver.get("http://www.cabelas.com/stores/stores_home.jsp")  
        # city = self.driver.find_element_by_id("address")
        # city.send_keys('Los Angeles')
        # self.driver.find_element_by_name("searchStore").click()
        # source = self.driver.page_source.encode("utf8")
        # tree = etree.HTML(source)
        # with open('response.html','wb') as f:
        #     f.write(source)
    
        # script_dir = os.path.dirname(__file__)
        # file_path = script_dir + '/geo/cities.json'
        # with open(file_path) as data_file:    
        #     location_list = json.load(data_file)
        # for location in location_list: 
        #     self.driver.get("http://tjmaxx.tjx.com/store/stores/storeLocator.jsp?")  
        #     if self.index == 0:
        #         self.driver.find_element_by_id("modal-close").click()
        #     self.index = self.index + 1                                
        #     city = self.driver.find_element_by_id("store-location-city")
        #     state = self.driver.find_element_by_id("store-location-state")
        #     city.send_keys(location['city'])
        #     state.send_keys(location['state'])
        #     if self.driver.find_element_by_name("submit") is not None:
        #         self.driver.find_element_by_name("submit").click()
        #     source = self.driver.page_source.encode("utf8")
        #     tree = etree.HTML(source)
        #     store_list = tree.xpath('//li[@class="store-list-item vcard address"]')
        #     for store in store_list:
        #         self.item['store_name'] = store.xpath('.//h3/text()')[0].strip()
        #         self.item['store_number'] = ''
        #         self.item['address'] = store.xpath('.//div[@class="adr"]//span[@class="street-address"]/text()')[0].strip()
        #         self.item['address2'] = ''
        #         self.item['city'] = store.xpath('.//div[@class="adr"]//span[@class="locality"]/text()')[0].strip()
        #         self.item['state'] = store.xpath('.//div[@class="adr"]//abbr[@class="region"]/text()')[0].strip()
        #         self.item['zip_code'] = store.xpath('.//div[@class="adr"]//span[@class="postal-code"]/text()')[0].strip()
        #         self.item['country'] = 'United States'
        #         self.item['phone_number'] = store.xpath('.//div[@class="tel"]/text()')[0].strip()
        #         self.item['latitude'] = ''
        #         self.item['longitude'] = ''
        #         self.item['store_hours'] = store.xpath('.//time/text()')[0].strip()
        #         self.item['store_type'] = ''
        #         self.item['other_fields'] = ''
        #         self.item['distributor_name'] = ''
        #         yield self.item