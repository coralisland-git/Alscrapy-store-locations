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

class quiksilver(scrapy.Spider):
	name = 'quiksilver'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.US_location_list = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.CA_location_list = json.load(data_file)

	def start_requests(self):
		location_list = self.US_location_list + self.CA_location_list
		for location in location_list:
			init_url = 'http://www.quiksilver.com/on/demandware.store/Sites-QS-US-Site/en_US/StoreLocator-StoreLookup?latitude='+str(location['latitude'])+'&longitude='+str(location['longitude'])+'&loyaltyMemberProgram=0'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['stores']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = store['ID']
			item['address'] = store['address']
			item['city'] = store['city']
			item['zip_code'] = store['postalCode']
			try:
				zip_code = int(item['zip_code'][-3:])
				item['country'] = 'United States'
			except:
				item['country'] = 'Canada'
			item['phone_number'] = store['phone']
			if item['phone_number'] == 'NULL':
				item['phone_number'] = ''
			item['latitude'] = str(store['latitude'])
			item['longitude'] = str(store['longitude'])
			h_temp = ''
			hour_list = store['storeHours']
			for hour in hour_list:
				if hour[1] != '-':
					h_temp += hour[0] + ' ' + hour[1] + ', '
			item['store_hours'] = h_temp[:-2]
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''