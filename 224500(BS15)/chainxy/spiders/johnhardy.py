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

class johnhardy(scrapy.Spider):
	name = 'johnhardy'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.johnhardy.com/on/demandware.store/Sites-johnhardy-Site/default/Stores-FindByState?state=%s' %location['abbreviation']
			header = {
				"Accept":"*/*",
				"Accept-Encoding":"gzip, deflate, sdch",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['name'])
					item['store_number'] = self.validate(store['storeID'])
					item['address'] = self.validate(store['address1'])
					item['address2'] = self.validate(store['address2'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['stateCode'])
					item['zip_code'] = self.validate(store['postalCode'])
					item['country'] = self.validate(store['countryCode'])
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(store['latitude'])
					item['longitude'] = self.validate(store['longitude'])
					item['store_hours'] = self.validate(store['storeHours'])
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('null','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp
