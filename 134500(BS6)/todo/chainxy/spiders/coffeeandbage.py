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

class coffeeandbage(scrapy.Spider):
	name = 'coffeeandbage'
	domain = 'www.coffeeandbagels.com'
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'https://api.donde.io/near?callback=jQuery110205648670967553304_1494246139719&center=37.020098201368114,-98.76708984374999&limit=500&dondeKey=5727975c19d21c000b000004&_=1494246139721'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = '[' + response.body.split('([')[1][:-2]
		store_list = json.loads(data)
		for store in store_list:
			item = ChainItem()
			name = self.validate(store['name'])
			item['coming_soon'] = ''
			if 'coming soon' in name.lower():
				name = self.validate(name.split('-')[1])
				item['coming_soon'] = '1'
			item['store_name'] = name
			item['store_number'] = self.validate(store['corporate_id'])
			item['address'] = self.validate(store['street'])
			item['address2'] = self.validate(store['address_line_2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = self.validate(store['country'])
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(str(store['Location']['coordinates'][1]))
			item['longitude'] = self.validate(str(store['Location']['coordinates'][0]))
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item			

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''