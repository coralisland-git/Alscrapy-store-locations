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

class autoparts2020(scrapy.Spider):
	name = 'autoparts2020'
	domain = ''
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.autoparts2020.com/locations/storeLocator/stores/service/10/500/'+location['city']
			header = {
				"Accept":"application/json, text/plain, */*",
				"Accept-Encoding":"gzip, deflate, br"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['hits']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['businessName'])
					item['store_number'] = self.validate(str(store['businessEntityId']))
					item['address'] = self.validate(store['address'])	
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['postalCode'])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(store['phoneNumber'])
					item['latitude'] = self.validate(str(store['latitude']))
					item['longitude'] = self.validate(str(store['longitude']))
					h_temp = ''
					try:
						hour_list = store['businessHours']
						for hour in hour_list:
							try:
								h_temp += hour['dayOfWeek'] + ' ' + hour['timeOpen'] + '-' + hour['timeClose'] + ', '
							except:
								pass
						item['store_hours'] = h_temp[:-2]
					except:
						pass
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pass
		except:
			pass

	def validate(self, item):
		try:
			if item.strip() == 'None':
				return ''
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp