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

class monro(scrapy.Spider):
	name = 'monro'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_States.json'
		with open(file_path) as data_file:    
			self.US_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.monro.com/WebServices/LocationSearchService.asmx/GetStoresWithinDistanceByBrand'
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/json; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			payload = {
				"distanceMiles":"0",
				"latitude":str(location['latitude']),
				"longitude":str(location['longitude']),
				"stateCode":self.get_state(location['state'])
			}
			yield scrapy.Request(url=init_url, body=json.dumps(payload), headers=header, method='post', callback=self.body)

	def body(self, response):
		store_list = json.loads(response.body)
		store_list = json.loads(store_list['d'])
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['Name'])
				item['store_number'] = self.validate(str(store['Id']))
				item['address'] = self.validate(store['Address'])
				item['city'] = self.validate(store['City'])
				item['state'] = self.validate(store['StateCode'])
				item['country'] = 'United States'
				item['zip_code'] = self.validate(str(store['ZipCode']))
				item['phone_number'] = self.validate(store['Phone'])
				item['latitude'] = self.validate(str(store['Latitude']))
				item['longitude'] = self.validate(str(store['Longitude']))
				h_temp = ''
				week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
				for week in week_list:
					try:
						h_temp += week + ' ' + store[week+'Hours'] + ', '
					except:
						pass
				item['store_hours'] = h_temp[:-2]
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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def check_country(self, item):
		if 'PR' in item:
			return 'Puert Rico'
		else:
			for state in self.US_States_list:
				if item in state['abbreviation']:
					return 'United States'
			return 'Canada'

	def get_state(self, item):
		for state in self.US_States_list:
			if item.lower() in state['name'].lower():
				return state['abbreviation']
		return ''