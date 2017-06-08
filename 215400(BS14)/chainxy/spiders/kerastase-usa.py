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

class kerastaseusa(scrapy.Spider):
	name = 'kerastase-usa'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://storelocator.api.lorealebusiness.com//api/SalonFinderservice/GetSalonFinderstores'
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			formdata = {
				"radius":"100",
				"StoreName":"",
				"storesperpage":"5",
				"pagenum":"",
				"latitude":str(location['latitude']),
				"longitude":str(location['longitude']),
				"brand":"Kerastase",
				"Nametype":"N"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		try:
			store_list = json.loads(response.body)[0]['Stores']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['SalonName'])
					item['store_number'] = self.validate(str(store['StoreID']))
					item['address'] = self.validate(store['Address'])
					item['city'] = self.validate(store['City'])
					item['state'] = self.validate(store['State'])
					item['zip_code'] = self.validate(store['ZipCode'])
					item['country'] = "United States"
					item['phone_number'] = self.validate(store['Phone'])
					item['latitude'] = self.validate(str(store['Latitude']))
					item['longitude'] = self.validate(str(store['Longitude']))
					item['store_hours'] = self.validate(store['workingHours'])
					item['store_type'] = self.validate(store['Type'])
					item['other_fields'] = ''
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