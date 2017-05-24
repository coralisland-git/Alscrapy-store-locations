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

class bp(scrapy.Spider):
	name = 'bp'
	domain = 'https://www.mybpstation.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.mybpstation.com/station-finder/json/%s--%s/%s---%s' % (str(location['latitude']), str(location['latitude']+0.432), str(location['longitude']), str(location['longitude']+0.562))
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			store_list = json.loads(response.body)['features']
			for store in store_list:
				item = ChainItem()
				item['store_name'] = self.validate(store['properties']['name'])
				item['store_number'] = self.validate(str(store['properties']['nid']))
				item['address'] = self.validate(store['properties']['thoroughfare'])
				item['city'] = self.validate(store['properties']['localty'])
				item['state'] = self.validate(store['properties']['state_code'])
				item['zip_code'] = self.validate(str(store['properties']['postal_code']))
				if len(item['zip_code']) > 6:
					item['zip_code'] = item['zip_code'][:-4] + '-' + item['zip_code'][-4:]
				item['country'] = 'United States'
				item['phone_number'] = self.validate(str(store['properties']['phone']))
				if item['phone_number'] == 'None':
					item['phone_number'] = ''
				item['latitude'] = self.validate(str(store['geometry']['coordinates'][0]))
				item['longitude'] = self.validate(str(store['geometry']['coordinates'][1]))
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
					yield item		
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip().replace(';','')
		except:
			return ''