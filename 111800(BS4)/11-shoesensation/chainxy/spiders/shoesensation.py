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

class shoesensation(scrapy.Spider):
	name = 'shoesensation'
	domain = 'https://www.shoesensation.com/'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		
		init_url = 'https://www.shoesensation.com/storelocator/index/loadstore/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['storesjson']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['store_name'][:-3]
			item['store_number'] = store['store_name'][-3:]
			address = store['address']
			item['address'] = address
			item['address2'] = ''
			if ',' in address:
				address = address.split(',')
				item['address'] = address[0]
				item['address2'] = address[1]
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['zipcode']
			item['country'] = store['country_id']
			item['phone_number'] = store['phone']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			h_temp = ''
			week_list = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
			for week in week_list:
				try:
					h_temp += week + ' ' + store[week] + ', '
				except:
					pass
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''