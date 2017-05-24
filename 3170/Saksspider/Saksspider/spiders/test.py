import scrapy, time
import selenium
from selenium import webdriver
from lxml import etree
import os
import json

class testspider(scrapy.Spider):
    name = "testspider"
    item = {}    

    def start_requests(self):
        self.driver = webdriver.Chrome("./chromedriver") 
        self.driver.get("http://www.saksfifthavenue.com/stores/stores.jsp")  
        time.sleep(5)
        # self.driver.find_element_by_id("close-button").click()
        city = self.driver.find_element_by_id("storesCity")
        state = self.driver.find_element_by_id("storesState_input")
        city.send_keys("Los Angeles")
        state.send_keys("California")
        self.driver.find_element_by_id("btnSearchStores").click()
        source = self.driver.page_source.encode("utf8")
        with open('res10.html', 'wb') as f:
            f.write(source)
