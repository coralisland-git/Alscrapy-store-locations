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

class pizzahut(scrapy.Spider):
	name = 'pizzahut'
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
		# for location in self.location_list:
		try:
			init_url = 'https://www.pizzahut.com/api.php/site/api_ajax/search/carryout'
			# init_url = 'https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?postalCode='+str(self.get_zipcode(location['city'])['zipcode'])+'&countryCode=US&distanceUnit=imperial&maxdistance=100&carters=false&oshkosh=true&lat='+str(self.get_zipcode(location['city'])['latitude'])+'&lng='+str(self.get_zipcode(location['city'])['longitude'])
			header = {
				"accept":"application/json, text/plain, */*",
				"accept-encoding":"gzip, deflate, br",
				"content-type":"application/json;charset=UTF-8"
			}
			payload = {
				"customer_postal_code" : "90001",
				"limit":"9"
			}
			yield scrapy.Request(url=init_url, headers=header, body=json.dumps(payload), method='post', callback=self.body) 
		except:
			pass

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)
		try:
			store_list = json.loads(response.body)['response']
			pdb.set_trace()
			for store in store_list:
				try:
					item = ChainItem()
					item['store_number'] = self.validate(store['StoreNumber'])
					item['address'] = self.validate(store['address'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['zip'])
					item['country'] = self.validate(store['country'])
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(str(store['lat']))
					item['longitude'] = self.validate(str(store['long']))
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						yield item	
				except:
					pdb.set_trace()
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