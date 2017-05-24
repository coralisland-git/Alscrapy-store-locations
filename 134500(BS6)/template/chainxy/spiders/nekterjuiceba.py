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


class nekterjuiceba(scrapy.Spider):
	name = 'nekterjuiceba'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'ttps://momentfeed-prod.apigee.net/api/llp.json?auth_token=YFPOHLGEBGSKZZOW&coordinates=-9.96885060854611,-61.69921875,70.4367988185464,-130.4296875&pageSize=50'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):

		print("=========  Checking.......")
		# store_list = json.loads(response.body)
		# pdb.set_trace()
		# for store in store_list:
		# 	item = ChainItem()
		# 	item['store_name'] = self.validate(store['name'])
		# 	item['store_number'] = self.validate(store['store_number'])
		# 	item['address'] = self.validate(store['address'])
		# 	item['address2'] = self.validate(store['crossStreet'])
		# 	item['city'] = self.validate(store['city'])
		# 	item['state'] = self.validate(store['state'])
		# 	item['zip_code'] = self.validate(store['zip'])
		# 	item['country'] = self.validate(store['country'])
		# 	item['phone_number'] = self.validate(store['phone'])
		# 	item['latitude'] = self.validate(store['latitude'])
		# 	item['longitude'] = self.validate(store['longitude'])
		# 	item['store_hours'] = self.validate(store['hours'])
		# 	item['store_type'] = ''
		# 	item['other_fields'] = ''
		# 	item['coming_soon'] = ''
		# 	if item['store_number'] not in self.history:
		# 		self.history.append(item['store_number'])
		# 		yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''