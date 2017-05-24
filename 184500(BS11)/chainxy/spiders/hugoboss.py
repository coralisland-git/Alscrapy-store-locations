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

class hugoboss(scrapy.Spider):
	name = 'hugoboss'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/All_Countries.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'http://production-web-hugo.demandware.net/s/UK/dw/shop/v16_9/stores?client_id=871c988f-3549-4d76-b200-8e33df5b45ba&latitude=%s&longitude=%s&count=200' %(str(location['latlng'][0]), str(location['latlng'][1]))
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['data']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(store['id'])
				item['address'] = self.validate(store['address1'])				
				item['city'] = self.validate(store['city'])
				try:
					item['state'] = self.validate(store['state'])
				except:
					pass
				try:
					item['zip_code'] = self.validate(store['postal_code'])
				except:
					pass
				item['country'] = self.check_country(self.validate(store['country_code']))
				item['latitude'] = self.validate(str(store['latitude']))
				item['longitude'] = self.validate(str(store['longitude']))
				h_temp = ''
				week_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
				try:
					hour_list = json.loads(self.validate(store['store_hours']))
					for hour in hour_list:
						h_temp += week_list[int(hour)-1] + ' ' + hour_list[hour][0] + '-' + hour_list[hour][1] +', '
					item['store_hours'] = h_temp[:-2]
				except:
					pass
				item['store_type'] = self.validate(store['_type'])
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
					yield item	
			except:
				pdb.set_trace()		

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

	def check_country(self, item):
		for country in self.location_list:
			if item in country['cca2']:
				return country['name']['common']
		return ''