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

class petsenseonline(scrapy.Spider):
	name = 'petsenseonline'
	domain = 'http://petsenseonline.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.easylocator.net/ajax/search_by_lat_lon/Petsense%20Store%20Locator/'+str(location['latitude'])+'/'+str(location['longitude'])+'/'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['physical']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = store['location_number']
			item['address'] = store['street_address']
			item['address2'] = store['street_address_line2']
			item['city'] = store['city']
			item['state'] = store['state_province']
			item['zip_code'] = store['zip_postal_code']
			item['country'] = store['country']
			item['phone_number'] = store['phone']
			item['latitude'] = store['lat']
			item['longitude'] = store['lon']
			h_temp = ''
			hour_list =store['additional_info'].split('<br />')
			if len(hour_list) > 2:
				item['store_hours'] = hour_list[1] + ', ' + hour_list[2]
			else :
				pass
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