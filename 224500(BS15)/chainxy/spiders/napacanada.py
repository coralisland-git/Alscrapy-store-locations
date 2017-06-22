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

class napacanada(scrapy.Spider):
	name = 'napacanada'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.kumhousa.com'
		yield scrapy.Request(url=init_url, callback=self.body)

	def body(self, response):
		self.driver.get("https://www.napacanada.com/en/find-a-napa-store")
		time.sleep(1)
		self.driver.find_element_by_id('change-my-store-link').click()
		source_list = []
		for location in self.location_list:
			try:
				search_text = self.driver.find_element_by_id('store-search-input')
				search_text.clear()
				search_text.send_keys(location['city'].split('(')[0].strip())
				time.sleep(1)
				self.driver.find_element_by_id('store-search-button').click()
				time.sleep(3)
				source = self.driver.page_source.encode("utf8")
				tree = etree.HTML(source)
				store_list = tree.xpath('//div[@class="store-information"]//ul/li')
				pdb.set_trace()
				if store_list:
					source_list.append(store_list)
			except:
				pass

		for source in source_list:
			for store in source:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store.xpath('.//div[@class="title-2"]/text()')[0])
					item['address'] = self.validate(store.xpath('.//div[@class="address-1"]/text()')[0])
					address = self.validate(store.xpath('.//div[@class="address-2"][2]/text()')[0])
					addr = address.split(',')
					item['city'] = self.validate(addr[0].strip())
					item['state'] = self.validate(addr[1].strip()[:2])
					item['zip_code'] = self.validate(addr[1].strip()[2:])
					item['country'] = 'Canada'
					item['phone_number'] = self.validate(store.xpath('.//div[@class="phone"]/text()')[0])
					h_temp = ''
					hour_list = self.eliminate_space(store.xpath('.//div[@class="store-listing-hours"]//text()'))
					cnt = 1
					for hour in hour_list:
						h_temp += hour
						if cnt % 2 == 0:
							h_temp += ', '
						else:
							h_temp += ' '
						cnt += 1
					item['store_hours'] = h_temp[:-2]
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
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp