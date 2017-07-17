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

class crunch(scrapy.Spider):
	name = 'crunch'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.US_Zip_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			try:
				zipcode = str(self.get_zipcode(location['city'])['zipcode'])
				for ind in range(0, 5-len(zipcode)):
					zipcode = '0'+zipcode
				init_url = 'https://www.crunch.com/locations?zipcode='+zipcode
				header = {
					"Accept":"application/json, text/javascript, */*; q=0.01",
					"Accept-Encoding":"gzip, deflate, br",
					"X-Requested-With":"XMLHttpRequest"
				}
				yield scrapy.Request(url=init_url, headers=header, method='GET', callback=self.body) 
			except:
				pass

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(store['id'])
				item['address'] = self.validate(store['address']['address_1'])
				item['address2'] = self.validate(store['address']['address_2'])
				item['city'] = self.validate(store['address']['city'])
				item['state'] = self.validate(store['address']['state'])
				item['zip_code'] = self.validate(store['address']['zip'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(str(store['latitude']))
				item['longitude'] = self.validate(str(store['longitude']))
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

	def get_zipcode(self, item):
		for zipcode in self.US_Zip_list:
			if item.lower() in zipcode['city'].lower():
				return zipcode
				break
		return ''