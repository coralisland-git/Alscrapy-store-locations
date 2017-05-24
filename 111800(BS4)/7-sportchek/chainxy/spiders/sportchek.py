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

class sportchek(scrapy.Spider):
	name = 'sportchek'
	domain = 'https://www.sportchek.ca'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			if '(' in location['city']:
				temp = location['city'].split('(')[0].strip()
			init_url = 'https://www.sportchek.ca/services/sportchek/stores?productIds=&locale=en&location=%s' % temp
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['results']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['title']
			item['store_number'] = store['name']
			item['address'] = store['address']['line2']
			item['address2'] = ''
			item['city'] = store['address']['town']
			item['state'] = store['address']['province']
			item['zip_code'] = store['address']['postalCode']
			item['country'] = 'Canada'
			item['phone_number'] = store['address']['phone']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			item['store_hours'] = store['workingTime']
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_name']+str(item['store_number']) not in self.history:
				self.history.append(item['store_name']+str(item['store_number']))
				yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''