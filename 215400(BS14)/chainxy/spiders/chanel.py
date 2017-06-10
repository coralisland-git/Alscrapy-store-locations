from __future__ import unicode_literals
import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import time
import usaddress

class chanel(scrapy.Spider):
	name = 'chanel'
	domain = ''
	history = []
	count = 0

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.US_location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.chanel.com'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		self.driver.get("https://services.chanel.com/en_US/storelocator/")
		source_list = []
		for location in self.US_location_list:
			search_text = self.driver.find_element_by_id('searchTextField')
			search_text.clear()
			search_text.send_keys(location['city'].upper())
			time.sleep(1)
			self.driver.find_element_by_id('leftSearchButton').click()
			time.sleep(3)
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source)
			time.sleep(1)
			store_list = tree.xpath('//div[@class="store-box"]')
			if store_list:
				source_list.append(store_list)

		for source in source_list:
			for store in source:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store.xpath('.//a[@class="store-box-title-link store-box-button"]/text()')[0])
					item['address'] = self.validate(store.xpath('.//address/text()')[0])
					address = self.validate(store.xpath('.//address//span[@class="zipcode"]/text()')[0]).split(',')
					item['city'] = self.validate(address[1])
					item['state'] = self.validate(address[2])
					item['zip_code'] = self.validate(address[0])
					item['country'] = 'United States'
					try:
						item['phone_number'] = self.validate(store.xpath('.//span[@class="phone"]/text()')[0])
					except:
						item['phone_number'] = ''

					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '' and 'STORE HOURS:' not in self.validate(item):
				tmp.append(self.validate(item))
		return tmp

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''