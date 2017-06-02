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

class nissanusa(scrapy.Spider):
	name = 'nissanusa'
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
		for location in self.location_list:
			init_url = 'https://www.nissanusa.com/nissandealers/locate/dealersAjax?channelCode=in&zipCode=&cityName='+location['city']+'&stateCode='+self.get_state(location['state'])+'&format=json'
			header = {
				"Accept":"*/*",
				"Accept-Encoding":"gzip, deflate, sdch, br",
				"X-Requested-With":"XMLHttpRequest"
			}
			yield scrapy.Request(url=init_url, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['dealers']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['name'])
					item['store_number'] = self.validate(store['dealerId'])
					item['address'] = self.validate(store['addressLine1'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(store['zipCode'])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(store['phoneNumber'])
					item['latitude'] = self.validate(store['latitude'])
					item['longitude'] = self.validate(store['longitude'])
					h_temp = 'salesHours: '
					for key, value in store['salesHours'].items():
						h_temp += value['days'] + ' ' + value['startingHour'][:2] + ':' + value['startingHour'][2:] + '-'
						h_temp += value['closingHour'][:2] + ':' + value['closingHour'][:2] + ', '
					h_temp += 'serviceHours: '
					for key, value in store['serviceHours'].items():
						h_temp += value['days'] + ' ' + value['startingHour'][:2] + ':' + value['startingHour'][2:] + '-'
						h_temp += value['closingHour'][:2] + ':' + value['closingHour'][:2] + ', '
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