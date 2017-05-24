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

class hooters(scrapy.Spider):
	name = 'hooters'
	domain = 'https://www.hooters.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url  = 'https://www.hooters.com/api/search_locations.json?address= %s' % location['city']
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):

		store_list = json.loads(response.body)
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = store['id']
			item['address'] = store['address']
			item['address2'] = ''
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['zip']
			item['country'] = store['country']
			item['phone_number'] = store['phone']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			item['store_hours'] = ''
			if store['weekday_hours'] != '':
				item['store_hours'] = 'Weekday ' + store['weekday_hours'] 
			if store['sunday_hours'] != '':
				item['store_hours'] += ', Sunday ' + store['sunday_hours']
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] in self.history:
				continue
			self.history.append(item['store_number'])
			if item['country'] == 'USA' or item['country'] == 'U. S. Virgin Islands':
				yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''