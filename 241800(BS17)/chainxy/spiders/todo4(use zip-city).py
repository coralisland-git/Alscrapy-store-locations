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

class todo4(scrapy.Spider):
	name = 'todo4'
	domain = ''
	history = []

	def __init__(self):
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
				init_url = 'https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?postalCode='+str(self.get_zipcode(location['city'])['zipcode'])+'&countryCode=US&distanceUnit=imperial&maxdistance=100&carters=false&oshkosh=true&lat='+str(self.get_zipcode(location['city'])['latitude'])+'&lng='+str(self.get_zipcode(location['city'])['longitude'])
				header = {
					"Accept":"application/json, text/javascript, */*; q=0.01",
					"Accept-Encoding":"gzip, deflate, sdch, br",
					"X-Requested-With":"XMLHttpRequest"
				}
				yield scrapy.Request(url=init_url, headers=header, callback=self.body) 
			except:
				pass

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['stores']
			for key, store in store_list.items():
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['mallName'])
					item['store_number'] = self.validate(store['storeid'])
					item['address'] = self.validate(store['address1'])
					item['address2'] = self.validate(store['address2'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['stateCode'])
					item['zip_code'] = self.validate(store['postalCode'])
					item['country'] = self.validate(store['countryCode'])
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(str(store['latitude']))
					item['longitude'] = self.validate(str(store['longitude']))
					h_temp = ''
					hour_list = self.eliminate_space(etree.HTML('<div>' + store['storeHours'] + '</div>').xpath('//text()'))[1:]
					cnt = 1
					for hour in hour_list:
						h_temp += hour
						if cnt % 2 == 0:
							h_temp += ', '
						else:
							h_temp += ' '
						cnt += 1
					item['store_hours'] = h_temp[:-2]
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
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

	def str_concat(self, items, unit):
		tmp = ''
		for item in items[:-1]:
			if self.validate(item) != '':
				tmp += self.validate(item) + unit
		tmp += self.validate(items[-1])
		return tmp

	def get_zipcode(self, item):
		for zipcode in self.US_Zip_list:
			if item.lower() in zipcode['city'].lower():
				return zipcode
				break
		return ''