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

class mydbsupply(scrapy.Spider):
	name = 'mydbsupply'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://mydbsupply.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		data = '[' + response.body.split(' stores: [')[1].strip().split('computed: {')[0].strip()[:-2].strip()[:-1].strip()
		store_list = json.loads(data)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['address'] = self.validate(store['street_address'])			
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'][1])
			item['zip_code'] = self.validate(store['postal'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			item['store_hours'] = self.validate(store['hours1'])
			try:
				item['store_hours'] += self.validate(store['hours2'])
			except:
				pass
			yield item			


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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''