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

class simplemobile(scrapy.Spider):
	name = 'simplemobile'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			"Accept":"*/*",
			"Accept-Encoding":"gzip, deflate, sdch, br"
		}
		for location in self.location_list:
			init_url = 'https://www.mapquestapi.com/search/v2/radius?callback=jQuery111205316341942255125_1495136608625&key=Gmjtd%7Cluub2qu2nu%2C85%3Do5-lzt2g&ambiguities=ignore&maxMatches=70&units=dm&hostedData=mqap.37706_sm_store_types%7C%7C%7CstoreName%2CstoreAdd%2CstoreCity%2CstoreState%2CstoreZip%2CstorePhone%2Cmqap_geography%2CstoreType%2CisBrandedRetailStore%2CisBoxedPhoneProgram%2CstoreList&radius=70&origin='+location['city']+'&_=1495136608631'
			yield scrapy.Request(url=init_url, headers=header, callback=self.body)  	

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body.split('jQuery111205316341942255125_1495136608625(')[1].strip()[:-2])['searchResults']
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['fields']['storeName'])
				item['address'] = self.validate(store['fields']['storeAdd'])
				item['city'] = self.validate(store['fields']['storeCity'])
				item['state'] = self.validate(store['fields']['storeState'])
				item['zip_code'] = self.validate(store['fields']['storeZip'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['fields']['storePhone'])
				item['latitude'] = self.validate(store['fields']['mqap_geography']['latLng']['lat'])
				item['longitude'] = self.validate(store['fields']['mqap_geography']['latLng']['lng'])
				item['store_type'] = self.validate(store['fields']['storeType'])
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