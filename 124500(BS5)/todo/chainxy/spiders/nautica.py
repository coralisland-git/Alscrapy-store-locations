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

class nautica(scrapy.Spider):
	name = 'nautica'
	domain = ''
	history = []

	def start_requests(self):
		formdata={
			'dwfrm_storelocator_country':'US',
			'dwfrm_storelocator_findbycountry':'Search'
		}
		header = {
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Encoding':'gzip, deflate, br',
			'Content-Type':'application/x-www-form-urlencoded'
		}
		init_url = 'https://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-Find/C289683342'
		yield scrapy.FormRequest(url=init_url, method='POST', formdata=formdata, headers=header, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)

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
			return item.strip()
		except:
			return ''