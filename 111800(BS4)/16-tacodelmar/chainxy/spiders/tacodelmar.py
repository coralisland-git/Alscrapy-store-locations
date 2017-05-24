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

class tacodelmar(scrapy.Spider):
	name = 'tacodelmar'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.US_location_list = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.CA_location_list = json.load(data_file)


	def start_requests(self):
		init_url = 'https://tacodelmar.com/wp-admin/admin-ajax.php'
		lists = [self.US_location_list, self.CA_location_list]
		for location_list in lists:
			for location in location_list:
				formdata = {
					'address': location['city'],
					'formdata':'addressInput='+location['city'],
					'lat':str(location['latitude']),
					'lng':str(location['longitude']),
					'count':'500',
					'distance':'500',
					'radius':'500',
					'action':'csl_ajax_search'
				}
				yield scrapy.FormRequest(url=init_url, formdata=formdata, method="POST", callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['response']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = store['name'].strip().replace('&amp;','')
				item['store_number'] = store['id']
				item['address'] = store['address'].strip()
				item['address2'] = store['address2'].strip()
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
					yield item		
			except:
				pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip().replace(';','').replace('&lt','').replace('&gt','').replace('/br',', ').replace('br',',').replace('\xe2','')
		except:
			return ''