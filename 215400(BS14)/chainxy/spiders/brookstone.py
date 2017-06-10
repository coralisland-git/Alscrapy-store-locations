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
import pdb

class brookstone(scrapy.Spider):
	name = 'brookstone'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://rembrandtcharms.com/pages/find-a-store'
		yield scrapy.Request(url=init_url, callback=self.body)
	
	def body(self, response):
		self.driver.get("http://www.brookstone.com/store-finder")
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		state_list = tree.xpath('//select[@id="dwfrm_storelocator_address_states_stateUSCA"]//option[contains(@class, "select-option")]/text()')
		source_list = []
		# self.driver.get("http://www.brookstone.com/store-finder")
		time.sleep(1)
		# self.driver.find_element_by_id('dwfrm_storelocator_address_states_stateUSCA').send_keys('Alabama')
		self.driver.find_element_by_name('dwfrm_storelocator_findbystate').click()
		pdb.set_trace()
		# time.sleep(5)
		# source = self.driver.page_source.encode("utf8")
		# tree = etree.HTML(source)
		# with open('response.html', 'wb') as f:
		# 	f.write(source)

		# for state in state_list[1:]:
		# 	try:
		# 		self.driver.get("http://www.brookstone.com/store-finder")
		# 		self.driver.find_element_by_id('dwfrm_storelocator_address_states_stateUSCA').send_keys(state)
		# 		self.driver.find_element_by_name('dwfrm_storelocator_findbystate').click()
		# 		time.sleep(10)
		# 		source = self.driver.page_source.encode("utf8")
		# 		tree = etree.HTML(source)
		# 		with open('response.html', 'wb') as f:
		# 			f.write(source)
		# 		store_list = tree.xpath('//div[@class="stores"]//div[contains(@class, "store flex blocks-1x3")]')
		# 		if store_list:
		# 			source_list.append(store_list)

		# 		if len(source_list) == 1:
		# 			break
		# 	except:
		# 		pdb.set_trace()

		# for source in source_list:
		# 	for store in source:
		# 		try:
		# 			item = ChainItem()
		# 			item['store_name'] = self.validate(store.xpath('.//div[@class="store-name"]/text()')[0].split('(')[0])
		# 			detail = self.eliminate_space(store.xpath('.//div[@class="store-address"]//text()'))
		# 			item['address'] = detail[0]
		# 			address = detail[1].split(',')
		# 			item['city'] = self.validate(address[0].strip())
		# 			item['state'] = self.validate(address[1].strip().split(' ')[0].strip())
		# 			item['zip_code'] = self.validate(address[1].strip().split(' ')[1].strip())
		# 			item['country'] = detail[2]
		# 			item['phone_number'] = detail[3]
		# 			hour_list = self.eliminate_space(store.xpath('.//div[@class="popDetailsHours"]//text()'))
		# 			h_temp = ''
		# 			item['store_hours'] = self.validate(store.xpath('.//div[@class="store-hours"]//text()'))
		# 			for hour in hour_list:
		# 				h_temp += hour + ', '
		# 			item['store_hours'] = h_temp[:-2]
		# 			if item['address']+item['phone_number'] not in self.history:
		# 				self.history.append(item['address']+item['phone_number'])
		# 				yield item	
		# 		except:
		# 			pdb.set_trace()

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