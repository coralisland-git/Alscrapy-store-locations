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
import usaddress

class faconnable(scrapy.Spider):
	name = 'faconnable'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.faconnable.com/en/storelocator/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="section group store"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h3[@class="store_name"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//p[@class="address"]//span[1]/text()').extract_first())				
				item['city'] = self.validate(store.xpath('.//p[@class="address"]//span[2]/text()').extract_first()).split(',')[0]
				item['state'] = self.validate(store.xpath('./@data-region').extract_first())
				item['zip_code'] = self.validate(store.xpath('.//p[@class="address"]//span[2]/text()').extract_first()).split(',')[1]
				item['country'] = self.validate(store.xpath('./@data-country').extract_first())
				item['phone_number'] = self.validate(store.xpath('.//p[@class="phone"]/text()').extract_first())
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
