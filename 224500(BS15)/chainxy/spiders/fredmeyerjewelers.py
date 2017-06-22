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

class fredmeyerjewelers(scrapy.Spider):
	name = 'fredmeyerjewelers'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.fredmeyerjewelers.com/Service/storelocatorhandler.ashx?action=FindStores&zipCode=&city='+location['city']+'&state='+self.get_state(location['state'])+'&radius=100'
			header = {
				"Accept":"text/javascript, text/html, application/xml, text/xml, */*",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		try:
			store_list = json.loads(response.body)
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['StoreName'])
					item['store_number'] = self.validate(store['RecordId'])
					item['address'] = self.validate(store['AddressLine1'])
					item['address2'] = self.validate(store['AddressLine2'])
					item['city'] = self.validate(store['City'])
					item['state'] = self.validate(store['State'])
					item['zip_code'] = self.validate(store['ZipCode'])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(store['Phone'])
					item['latitude'] = self.validate(str(store['Latitude']))
					item['longitude'] = self.validate(str(store['Longitude']))
					h_temp = ''
					week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
					for week in week_list:
						try:
							h_temp += week + ' ' + store['StoreHours'][week+'Open'] + '-' + store['StoreHours'][week+'Close'] + ', '
						except:
							pass
					item['store_hours'] = h_temp[:-2]
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						if 'Fred Meyer' in item['store_name']:
							yield item	

				except:
					pass	
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

	def get_state(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''