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

class discountdrugmart(scrapy.Spider):
	name = 'discountdrugmart'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://discount-drugmart.com/our-store/store-locator/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.body.split('var stores =')[1].strip().split('var stores_meta =')[0].strip()[:-1]
		store_list = json.loads(data)	
		for store in store_list:
			item = ChainItem()
			item['store_name'] = 'Discount Drug Mart'
			item['store_number'] = self.validate(store['store'])
			item['address'] = self.validate(store['address'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			item['store_hours'] = 'Store Hours : ' + self.validate(store['store_hours']) + ' Pharmacy Hours : ' + self.validate(store['pharmacy_hours'])
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
