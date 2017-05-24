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

class only(scrapy.Spider):
	name = 'only'
	domain = 'https://www.99only.com/'
	history = ['']

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url  = 'http://99only.com/storeservices.php?distance=100&lat='+str(location['latitude'])+'&lng='+str(location['longitude'])
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['stores']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = store['ID']
			item['address'] = store['address']
			item['address2'] = store['crossStreet']
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['zip']
			item['country'] = 'United States'
			item['phone_number'] = store['phone']
			item['latitude'] = store['lat']
			item['longitude'] = store['lng']
			item['store_hours'] = 'Mon ' + store['monday'] + ', Tue ' + store['tuesday'] + ', Wed ' + store['wednesday'] + ', Thu ' + store['thursday'] + ', Fri ' + store['friday'] + ', Sat ' + store['saturday'] + ', Sun ' + store['sunday']
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] in self.history:
				continue
			self.history.append(item['store_number'])
			yield item	


	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''