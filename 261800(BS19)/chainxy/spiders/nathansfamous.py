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
import pdb

class nathansfamous(scrapy.Spider):
	name = 'nathansfamous'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Zipcode.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			zipcode = str(location['zipcode'])
			for ind in range(0, 5-len(zipcode)):
				zipcode = '0'+zipcode
			init_url = 'https://locator.smfmsvc.com/api/v1/locations?client_id=156&brand_id=ACTP&product_id=NATHALL&product_type=agg&zip='+zipcode+'&search_radius=100'
			header = {
				"accept":"*/*",
				"accept-encoding":"gzip, deflate, br"
			}
			yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['RESULTS']['STORES']['STORE']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['NAME'])
				item['store_number'] = self.validate(store['STORE_ID'])
				item['address'] = self.validate(store['ADDRESS'])				
				item['city'] = self.validate(store['CITY'])
				item['state'] = self.validate(store['STATE'])
				item['zip_code'] = self.validate(store['ZIP'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['PHONE'])
				item['latitude'] = self.validate(store['LATITUDE'])
				item['longitude'] = self.validate(store['LONGITUDE'])
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
					yield item	
			except:
				pdb.set_trace()		

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