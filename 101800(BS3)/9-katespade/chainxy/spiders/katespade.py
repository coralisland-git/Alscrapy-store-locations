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

class katespade(scrapy.Spider):
	name = 'katespade'
	domain = 'https://www.katespade.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):

		init_url  = 'https://www.katespade.com/stores/en/api/v2/stores.json?instart_disable_injection=true'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		# with open('response.html', 'wb') as f:
		# 	f.write(response.body)

		store_list = json.loads(response.body)['stores']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['store_number'] = self.validate(store['number'])
			item['address'] = self.validate(store['address_1'])
			item['address2'] = self.validate(store['address_2'])
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['postal_code']
			item['country'] = store['country_code']
			item['phone_number'] = store['phone_number']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			h_temp = ''
			store_list = store['regular_hour_ranges']
			for store in store_list:
				h_temp += self.validate(store['days']) + ' ' + self.validate(store['hours']) + ', '
			item['store_hours'] = h_temp.strip()[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item			

	def validate(self, item):
		try:
 			return item.strip().replace('\n', '').replace('&#8211', '-').replace(';','').replace('<br/>', '')
		except:
			return ''