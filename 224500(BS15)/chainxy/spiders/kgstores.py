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

class kgstores(scrapy.Spider):
	name = 'kgstores'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.kgstores.com/kg/store/'+str(location['latitude'])+'%7C'+str(location['longitude'])+'.json'
			header = {
				"Accept":"application/json, text/javascript, */*; q=0.01",
				"Accept-Encoding":"gzip, deflate, br",
				"Content-Type":"application/json; charset=UTF-8",
				"X-Requested-With":"XMLHttpRequest"
			}
			payload = str(location['latitude']) + '|' + str(location['longitude'])
			yield scrapy.Request(url=init_url, headers=header, body=payload, method='post', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['storeName'])[5:].strip()
					item['store_number'] = self.validate(str(store['stlocId']))
					item['address'] = self.validate(store['address1'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['zipcode'])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(store['latitude'])
					item['longitude'] = self.validate(store['longitude'])
					item['store_hours'] = self.validate(store['hours'])
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('<br>',', ')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp