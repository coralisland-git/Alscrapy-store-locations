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
import pdb

class quiksilver(scrapy.Spider):
	name = 'quiksilver'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/geolocation.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://www.quiksilver.com/s/QS-US/dw/shop/v15_9/stores?latitude='+str(location['latitude'])+'&longitude='+str(location['longitude'])+'&country_code=US&distance_unit=MI&max_distance=5000&client_id=13d00e86-f1e5-4c51-abf5-af0c25ebf069'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['data']
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = store['name']
					item['store_number'] = store['id']
					item['address'] = store['address1']
					try:
						item['address2'] = store['address2']
					except:
						pass
					try:
						item['city'] = store['city']
					except:
						pass
					try:
						item['state'] = store['state_code']
					except:
						pass
					try:
						item['zip_code'] = store['postal_code']
					except:
						pass
					try:
						item['country'] = store['country_code']
					except:
						pass
					try:
						item['latitude'] = store['latitude']
					except:
						pass
					try:
						item['longitude'] = store['longitude']
					except:
						pass
					try:
						item['store_type'] = store['_type']
					except:
						pass
					if item['store_number'] not in self.history:
						self.history.append(item['store_number'])
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