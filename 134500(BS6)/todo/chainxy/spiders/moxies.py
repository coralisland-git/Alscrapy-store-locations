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
import unicodedata

class moxies(scrapy.Spider):
	name = 'moxies'
	domain = 'https://moxies.com/'
	history = []

	def __init__(self, *args, **kwargs):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)
		file_path = script_dir + '/geo/US_CA_States.json'
		with open(file_path) as data_file:    
			self.US_CA_States_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://moxies.com/all-locations/json'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = json.loads(response.body)['nodes']
		for store in store_list:
			store = store['node']
			item = ChainItem()
			item['store_name'] = self.validate(store['Label'])
			item['store_number'] = self.validate(store['Locations ID'])
			item['address'] = self.validate(store['Street']).replace('<br />',' , ')
			item['city'] = self.validate(store['City'])
			item['state'] = self.validate(store['Province'])
			item['zip_code'] = self.validate(store['PostalCode'])
			item['country'] = self.check_country(item['state'])
			item['phone_number'] = self.validate(store['Phone'])
			item['latitude'] = self.validate(store['Latitude'])
			item['longitude'] = self.validate(store['Longitude'])
			h_temp = ''	
			try:
				hour_list = etree.HTML(self.validate(store['Hours'])).xpath('//table//tr')
				for hour in hour_list:
					h_temp += hour.xpath('.//td[1]/text()')[0] + ' ' + hour.xpath('.//td[2]//text()')[0] + ', '
				item['store_hours'] = h_temp[:-2]
			except:
				item['store_hours'] = ''	
			yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip().replace(';', '')
		except:
			return ''

	def check_country(self, item):
		for state in self.US_CA_States_list:
			if item.lower() in state['abbreviation'].lower():
				return state['country']
		return ''