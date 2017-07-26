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
import usaddress

class test(scrapy.Spider):
	name = 'test'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.mapcorewards.com/store-locator/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			data = response.body.split(' var mapData = ')[1].strip().split('mapData.forEach')[0].strip()[:-1]
			store_list = json.loads(data)
			for store in store_list:
				try:
					item = ChainItem()
					item['store_name'] = self.validate(store['Title'])
					item['store_number'] = self.validate(str(store['Id']))
					item['address'] = self.validate(store['Address'])				
					item['city'] = self.validate(store['City'])
					item['state'] = self.validate(store['State'])
					item['zip_code'] = self.validate(store['Zipcode'])
					item['country'] = 'United States'
					item['phone_number'] = self.validate(store['Phone'])
					item['latitude'] = self.validate(str(store['Latitude']))
					item['longitude'] = self.validate(str(store['Longitude']))
					if 'MAPCO MART' in item['store_name']:
						yield item	
				except:
					pdb.set_trace()
		except:
			pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''