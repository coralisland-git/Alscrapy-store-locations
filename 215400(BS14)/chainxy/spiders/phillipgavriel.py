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

class phillipgavriel(scrapy.Spider):
	name = 'phillipgavriel'
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
		init_url = 'http://phillipgavriel.com/wp-admin/admin-ajax.php'
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			formdata = {
				"address":location['city'],
				"formdata":"addressInput="+location['city'],
				"lat":str(location['latitude']),
				"lng":str(location['longitude']),
				"name":"",
				"radius":"200",
				"tags":"",
				"action":"csl_ajax_search"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['response']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(store['id'])
				item['address'] = self.validate(store['address'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['state'])
				item['zip_code'] = self.validate(store['zip'])
				item['country'] = self.check_country(item['state'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				if item['address']+item['phone_number'] not in self.history:
					if item['country'] == 'US':
						self.history.append(item['address']+item['phone_number'])
					yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('&#039;', "'").replace(';','')
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
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''
