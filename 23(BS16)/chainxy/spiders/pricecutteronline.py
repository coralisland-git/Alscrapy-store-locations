from __future__ import unicode_literals
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

class pricecutteronline(scrapy.Spider):
	name = 'pricecutteronline'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://api.freshop.com/1/stores?limit=-1&has_address=true&token=3a1d2cc93a36d70e5f082c2d4533baa1&app_key=price_cutter'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['items']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(store['id'])
				item['address'] = self.validate(store['address_1'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['state'])
				item['zip_code'] = self.validate(store['postal_code'])
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store['phone']).split('\n')[0]
				item['latitude'] = str(self.validate(store['latitude']))
				item['longitude'] = str(self.validate(store['longitude']))
				try:
					item['store_hours'] = self.validate(store['hours'])
				except:
					pass
				yield item	
			except:
				pass	

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''