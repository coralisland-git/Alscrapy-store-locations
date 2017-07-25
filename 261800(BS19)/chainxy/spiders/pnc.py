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

class pnc(scrapy.Spider):
	name = 'pnc'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://apps.pnc.com/locator-api/locator/api/v2/location/?latitude='+str(location['latitude'])+'&longitude='+str(location['longitude'])+'&radius=100&radiusUnits=mi&branchesOpenNow=false'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['locations']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['locationName'])
				item['store_number'] = self.validate(str(store['id']))
				item['address'] = self.validate(store['address']['address1'])
				item['address2'] = self.validate(store['address']['address2'])
				item['city'] = self.validate(store['address']['city'])
				item['state'] = self.validate(store['address']['state'])
				item['zip_code'] = self.validate(store['address']['zip'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['contactInfo'])
				item['latitude'] = self.validate(str(store['address']['latitude']))
				item['longitude'] = self.validate(str(store['address']['longitude']))
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