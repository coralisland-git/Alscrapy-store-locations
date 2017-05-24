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

class walgreens(scrapy.Spider):
	name = 'walgreens'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://customersearch.walgreens.com/storelocator/v1/stores/search'
		header = {
			"Accept":"application/json, text/plain, */*",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/json;charset=UTF-8"
		}
		for location in self.location_list:
			payload = {
				"lat":str(location['latitude']),
				"lng":str(location['longitude']),
				"p":"1",
				"r":"10",
				"requestType":"locator",
				"s":"15"
			}
			yield scrapy.Request(url=init_url, headers=header, method='post', body=json.dumps(payload), callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)['results']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_number'] = self.validate(store['store']['storeNumber'])
				item['address'] = self.validate(store['store']['address']['street'])
				item['city'] = self.validate(store['store']['address']['city'])
				item['state'] = self.validate(store['store']['address']['state'])
				item['zip_code'] = self.validate(store['store']['address']['zip'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['store']['phone'][0]['areaCode']) + self.validate(store['store']['phone'][0]['number'])
				item['latitude'] = self.validate(store['latitude'])
				item['longitude'] = self.validate(store['longitude'])
				if self.validate(store['store']['storeOpenTime']) == '12AM':
					item['store_hours'] = 'Store Hours : 24 hours, '
				else:
					item['store_hours'] = 'Store Hours : ' + self.validate(store['store']['storeOpenTime']) + '-' + self.validate(store['store']['storeCloseTime']) + ', '
				if self.validate(store['store']['pharmacyOpenTime']) == '12AM':
					item['store_hours'] += 'Pharmacy Hours: 24 hours'
				else:
					item['store_hours'] += 'Pharmacy Hours: ' + self.validate(store['store']['pharmacyOpenTime']) + '-' + self.validate(store['store']['pharmacyCloseTime'])
				item['store_type'] = self.validate(store['store']['storeType']) 
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
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
