import scrapy, time
import selenium
from selenium import webdriver
from lxml import etree
import os
import json

class carlsjr(scrapy.Spider):
    name = "carlsjr"
    item = {}   

    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver")
        self.index = 0

    def start_requests(self):
        init_url  = 'http://maps.carlsjr.com/stores/search?country=&q=San+Francisco&brand_id=2&center_lat=30.878432885402297&center_lng=-87.57302999999996&zoom=5'
        yield scrapy.Request(url=init_url, callback=self.parse)   
        
    def parse(self,response):       
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        for location in location_list: 
            self.driver.get('http://maps.carlsjr.com/stores/')
            city = self.driver.find_element_by_id("landingForm_q")
            city.send_keys('New York')
            self.driver.find_element_by_id("search").click()
            self.driver.get('http://maps.carlsjr.com/stores/search?q=New York&brand_id=2')
            source = self.driver.page_source.encode("utf8")
            tree = etree.HTML(source)
            store_list = tree.xpath('//li[@class="result"]')
            for store in store_list:
                try:
                    self.item['store_name'] = store.xpath('.//div[@class="media-bd"]//span[@class="location-info location-info_name"]/text()')[0].strip()
                    self.item['store_number'] = ''
                    a_temp = ''
                    for address in store.xpath('.//div[@class="media-bd"]//span[@class="location-info location-info_address"]'):
                        a_temp = a_temp + address.xpath('./text()')[0].strip() + ', '
                    self.item['address'] = store.xpath('.//div[@class="media-bd"]//span[@class="location-info location-info_address"][1]/text()')[0].strip()
                    self.item['address2'] = ''
                    addr = store.xpath('.//div[@class="media-bd"]//span[@class="location-info location-info_address"][2]/text()')[0].strip()
                    self.item['city'] = addr.split(',')[0].strip()
                    self.item['state'] = addr.split(',')[1].strip().split(' ')[0].strip()
                    self.item['zip_code'] = ''
                    if len(addr.split(',')[1].strip().split(' ')) >1:
                        self.item['zip_code'] = addr.split(',')[1].strip().split(' ')[1].strip()
                    self.item['country'] = 'United States'
                    self.item['phone_number'] = store.xpath('.//div[@class="media-bd"]//span[@class="location-info location-info_phone"]/text()')[0].strip()
                    self.item['latitude'] = ''
                    self.item['longitude'] = ''
                    h_temp = ''
                    hour_list = store.xpath('.//div[2]//div[@class="media"]//div[@class="media-bd media-bd_padding media-bd_border"]//ul[@class="vList vList_std vList_extraInfo"]//li')
                    for hour in hour_list:
                        h_temp = h_temp + hour.xpath('.//span[@class="inline-text_left ff-demi"]/text()')[0].strip() + hour.xpath('.//span[@class="inline-text_right ff-medium"]/text()')[0].strip() + ', '
                    self.item['store_hours'] = h_temp[:-2]
                    self.item['store_type'] = ''
                    self.item['other_fields'] = ''
                    self.item['distributor_name'] = ''
                    yield self.item
                except:
                    pass                