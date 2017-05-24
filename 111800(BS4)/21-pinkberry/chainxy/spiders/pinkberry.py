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

class pinkberry(scrapy.Spider):
	name = 'pinkberry'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://www.pinkberry.com/wp-admin/admin-ajax.php'
		for location in self.location_list:
			formdata = {
					'formdata':'addressInput=&addressInputCity='+location['city']+'&addressInputState='+location['state']+'&state_selector_discrete=on&addressInputCountry=United States&ignore_radius=0',
					'lat':str(location['latitude']),
					'lng':str(location['longitude']),
					'radius':'300',
					'action':'csl_ajax_search'
				}
			yield scrapy.FormRequest(url=init_url, formdata=formdata, method="POST", callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = json.loads(response.body)['response']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = store['id']
				item['address'] = self.validate(store['address'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = store['city']
				item['state'] = store['state']
				item['zip_code'] = store['zip']
				item['country'] = store['country']
				item['phone_number'] = store['phone']
				item['latitude'] = store['lat']
				item['longitude'] = store['lng']
				item['store_hours'] = self.validate(store['hours'])
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = ''
				if item['store_name']+str(item['store_number']) not in self.history:
					self.history.append(item['store_name']+str(item['store_number']))
					if item['country'] != 'Canada':
						yield item		
			except:
				pdb.set_trace()			

	def validate(self, item):
		try:
			return item.strip().replace(';', '')
		except:
			return ''