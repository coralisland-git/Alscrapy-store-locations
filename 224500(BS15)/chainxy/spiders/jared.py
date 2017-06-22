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

class jared(scrapy.Spider):
	name = 'jared'
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
		init_url = 'http://www.jared.com/AjaxStoreLocatorSearchView?storeId=10451&catalogId=10001&langId=-1&orderId='
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate",
			"Content-Type":"application/x-www-form-urlencoded",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.location_list:
			formdata = {
				"latitude":str(location['latitude']),
				"longitude":str(location['longitude']),
				"value":"50",
				"address":location['city'],
				"currentState":"DojoRefresh",
				"filterStoreId":"StoreId='10451' or StoreId='10511' or StoreId='10513'",
				"filterStoreName":"StoreName='Jared - Galleria of Jewelry' or StoreName='Jared Vault' or StoreName='Jared Jewelry Boutique'",
				"objectId":"",
				"requesttype":"ajax"
			}
			yield scrapy.FormRequest(url=init_url, headers=header, formdata=formdata, method='post', callback=self.body)

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = response.body.split('stloc.attribute = [];')
			for store in store_list[1:]:
				try:
					item = ChainItem()
					item['store_name'] = self.get_value(store, 'stloc.description[0].name =')
					item['store_number'] = self.get_value(store, 'stloc.attribute[0] =')
					item['address'] = self.get_value(store, 'stloc.locationInfo.address.addressLine[0] =')
					item['city'] = self.get_value(store, 'stloc.locationInfo.address.city =')
					item['state'] = self.get_value(store, 'stloc.locationInfo.address.stateOrProvinceName =')
					item['zip_code'] = self.get_value(store, 'stloc.locationInfo.address.postalCode =')
					item['country'] = 'United States'
					item['phone_number'] = self.get_value(store, 'stloc.locationInfo.telephone1.value =')
					item['latitude'] = self.get_value(store, 'stloc.locationInfo.geoCode.latitude =')
					item['longitude'] = self.get_value(store, 'stloc.locationInfo.geoCode.longitude =')
					item['store_hours'] = self.validate(self.get_value(store, 'stloc.hours ='))
					if item['address']+item['phone_number'] not in self.history:
						self.history.append(item['address']+item['phone_number'])
						if 'Jared - Galleria' in item['store_name']:
							yield item	
				except:
					pass	
		except:
			pass

	def validate(self, item):
		try:
			return item.strip().replace('<br>', ', ')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp

	def get_value(self, item, unit):
		try:
			return item.split(unit)[1].split(';')[0].strip().replace('"','').replace("'",'')
		except:
			return ''