import scrapy
import json
import csv
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

from selenium import webdriver
from lxml import html

class vitaminshoppe(scrapy.Spider):
	
	name = 'vitaminshoppe'
	domain = 'https://www.vitaminshoppe.com/'
	history = ['']

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):

		init_url  = 'https://www.vitaminshoppe.com/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):

		self.driver.get("https://www.vitaminshoppe.com/sl/storeLocator.jsp")  
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			location_list = json.load(data_file)
		for location in location_list:
			city = self.driver.find_element_by_name("/vitaminshoppe/commerce/locations/VsGeoLocatorFormHandler.address")
			city.clear()
			city.send_keys(location['city']+", "+location['state'])
			self.driver.find_element_by_id("FindLocation").click()
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			store_list = tree.xpath('//div[@class="block shadow results"]')
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = store.xpath('.//h4//a/text()')[0].strip().split(',')[0]
					item['store_number'] = ''
					address = store.xpath('.//span[@class="contact-info address extended"]/text()')
					item['address'] = address[0].strip()
					item['address2'] = ''
					if len(address) == 2:
						item['city'] = address[1].strip().split(',')[0]
						item['state'] = address[1].strip().split(',')[1].strip()[0:2]
						item['zip_code'] = address[1].strip().split(',')[1].strip()[3:]
					else :
						item['address2'] = address[1].strip()
						item['city'] = address[2].strip().split(',')[0]
						item['state'] = address[2].strip().split(',')[1].strip()[0:2]
						item['zip_code'] = address[2].strip().split(',')[1].strip()[3:]
					item['country'] = 'United States'
					item['phone_number'] = store.xpath('.//td[@class="tel bold padding-bottom10"]//a/text()')[0].strip() 
					item['latitude'] = ''
					item['longitude'] = ''
					item['store_hours'] = store.xpath('.//td[@class="contact-info timings padding-top0"]/text()')[0].strip() + ' ' + store.xpath('.//td[@class="contact-info timings padding-top0"]/text()')[1].strip()
					item['store_type'] = ''
					item['other_fields'] = ''
					item['coming_soon'] = ''
					if item['phone_number'] not in self.history:
						yield item
						self.history.append(item['phone_number'])
				except:
					pass
