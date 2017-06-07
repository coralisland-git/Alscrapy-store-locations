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

class kumon(scrapy.Spider):
	name = 'kumon'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.US_Cities_list = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.CA_Cities_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.kumon.com/Services/KumonWebService.asmx/GetCenterListByRadius'
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/json; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.US_Cities_list:
			payload = {
				"distanceUnit":"mi",
				"latitude":str(location['latitude']),
				"longitude":str(location['longitude']),
				"radius":"100"
			}
			yield scrapy.Request(url=init_url, headers=header, body=json.dumps(payload), method='post', callback=self.body) 
		for location in self.CA_Cities_list:
			payload = {
				"distanceUnit":"mi",
				"latitude":str(location['latitude']),
				"longitude":str(location['longitude']),
				"radius":"100"
			}
			yield scrapy.Request(url=init_url, headers=header, body=json.dumps(payload), method='post', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['d']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['CenterName'])
				item['address'] = self.validate(store['Address'])
				item['address2'] = self.validate(store['Address3'])
				item['city'] = self.validate(store['City'])
				item['state'] = self.validate(store['StateCode'])
				item['zip_code'] = self.validate(store['ZipCode'])
				item['country'] = self.validate(store['Country'])
				item['phone_number'] = self.validate(store['Phone'])
				item['latitude'] = self.validate(store['Lat'])
				item['longitude'] = self.validate(store['Lng'])
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
