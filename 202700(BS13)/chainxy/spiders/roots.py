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

class roots(scrapy.Spider):
	name = 'roots'
	domain = 'https://locations.cititrends.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)
	
	def start_requests(self):
		init_url  = 'http://www.roots.com/us/en/store-listing'
		yield scrapy.Request(url=init_url, callback=self.parse_state) 

	def parse_state(self, response):
		state_list = response.xpath('//div[@class="provincelistUS"]//a/@href').extract()
		for state in state_list:
			yield scrapy.Request(url=state, callback=self.parse_store)	

	def parse_store(self, response):
		store_list = response.xpath('//li[@class="learnmore"]//a/@href').extract()
		for store in store_list:
			store = store.replace('/us','/ca')
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//h1[@class="store-title"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = self.check_country(item['state'])
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
			item['store_hours'] = self.validate(response.xpath('//div[@class="jsondata"]/text()').extract_first())
			yield item			
		except:
			pass

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def validate(self, item):
		try:
			return item.strip().replace(';', ' ').replace('|', ', ')
		except:
			return ''