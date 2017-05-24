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

class pizzastudio(scrapy.Spider):
	name = 'pizzastudio'
	domain = 'https://pizzastudio.com/'
	history = []

	def start_requests(self):
		init_url = 'https://pizzastudio.com/stores.json'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['locationname'])
			try:
				item['address'] = self.validate(store['address1'])
			except:
				pass
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			try:
				item['zip_code'] = self.validate(str(store['zip']))
			except:
				pass
			item['country'] = 'United States'
			try:
				item['phone_number'] = self.validate(store['phone'])
			except:
				pass
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lon'])
			try:
				item['store_hours'] = self.validate(store['hours']).split('| <')[0]
				if '<p><a' in item['store_hours']:
					item['store_hours'] = item['store_hours'].split('<p><a')[0].strip()
			except:
				pass
			item['coming_soon'] = self.validate(store['comingsoon'])
			try:
				zip_code = int(item['zip_code'])
				yield item			
			except:
				pass
	def validate(self, item):
		try:
			return item.strip().replace('&nbsp;', ' ')
		except:
			return ''