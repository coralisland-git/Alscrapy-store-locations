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
import time
import usaddress

class coppel(scrapy.Spider):
	name = 'coppel'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://www.coppel.com/AjaxProvinceSelectionDisplayView?catalogId=10001&langId=-5&storeId=12761&instart_disable_injection=true'
		self.header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/x-www-form-urlencoded",
			"X-Requested-With":"XMLHttpRequest"
		}
		formdata = {
			"countryId":"11006",
			"objectId":"",
			"requesttype":"ajax"
		}
		yield scrapy.FormRequest(url=init_url, headers=self.header, formdata=formdata, method='post', callback=self.parse_state)		

	def parse_state(self, response):
		try:
			state_list = response.xpath('//select//option')
			for state in state_list:
				state_id = state.xpath('./@value').extract_first()
				state_name = state.xpath('./text()').extract_first()
				state_url = 'https://www.coppel.com/AjaxCitySelectionDisplayView?catalogId=10001&langId=-5&storeId=12761&instart_disable_injection=true'
				formdata = {
					"provinceId":state_id,
					"objectId":"",
					"requesttype":"ajax"
				}
				yield scrapy.FormRequest(url=state_url, headers=self.header, formdata=formdata, method='post', callback=self.parse_city, meta={'state':state_name})
		except:
			pass

	def parse_city(self, response):
		try:
			city_list = response.xpath('//select//option')
			for city in city_list:
				city_id = city.xpath('./@value').extract_first()
				city_name = city.xpath('./text()').extract_first()
				city_url = 'https://www.coppel.com/lookforStoreLocator?instart_disable_injection=true'
				formdata = {
					"obJson":'{"operation":"lookforStoreLocatorByCityName","cityName":'+city_name+',"stateName":'+response.meta["state"]+'}',
					"requesttype":"ajax",
				}
				yield scrapy.FormRequest(url=city_url, headers=self.header, formdata=formdata, method='post', callback=self.parse_store)
		except:
			pass

	def parse_store(self, response):
		try:
			data = response.body.strip()[2:-2].strip()
			store_list = json.loads(data)['storeLocatorResults']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['address3'])
					item['store_number'] = self.validate(store['identifier'])
					item['address'] = self.validate(store['address1'])
					item['city'] = self.validate(store['city'])
					item['state'] = self.validate(store['state'])
					item['zip_code'] = self.validate(str(store['zipCode']))
					if item['zip_code'] == 'None':
						item['zip_code'] = ''
					item['country'] = self.validate(store['country'])
					item['phone_number'] = self.validate(store['phone'])
					item['latitude'] = self.validate(store['latitude'])
					item['longitude'] = self.validate(store['longitude'])
					item['store_hours'] = self.validate(store['address2'])
					yield item	
				except:
					pass
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace(';','').replace('\u2013','')
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
