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

class ardianpharmacy(scrapy.Spider):
	name = 'ardian-pharmacy'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.guardian-pharmacy.ca/store-locator-ws/stores/search/2?swLatitude=41.84926553955628&swLongitude=-134.1641538125&neLatitude=66.55490696220748&neLongitude=-49.61337256249999'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['store_number'] = self.validate(store['id'])
			item['address'] = self.validate(store['address'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['provinceCode'])
			item['zip_code'] = self.validate(store['postalCode'])
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(str(store['latitude']))
			item['longitude'] = self.validate(str(store['longitude']))
			yield item			


	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp