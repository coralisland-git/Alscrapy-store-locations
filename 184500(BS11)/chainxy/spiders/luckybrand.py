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

class luckybrand(scrapy.Spider):
	name = 'luckybrand'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.luckybrand.com/on/demandware.store/Sites-LuckyBrand_v2-Site/en_US/Stores-GetStoresJSON?stateCode=%s' %location['abbreviation']
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(store['ID'])
				item['address'] = self.validate(store['address1'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['stateCode'])
				item['zip_code'] = self.validate(store['postalCode'])
				item['country'] = self.validate(store['country'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(str(store['latitude']))
				item['longitude'] = self.validate(str(store['longitude']))
				item['store_hours'] = self.validate(store['hours'])
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
