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

class northgatemarkets(scrapy.Spider):
	name = 'northgatemarkets'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.northgatemarkets.com/en-us/our-stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = '{'+response.body.split('storeInfoObj = {')[1].strip().split('var storeInfo')[0].strip()[:-1]
		store_list = json.loads(data)
		for store in store_list:
			store = store_list[store]
			item = ChainItem()
			item['store_number'] = self.validate(str(store['Id']))
			item['address'] = self.validate(store['full_address'])
			item['city'] = self.validate(store['City'])
			item['state'] = self.validate(store['State'])
			item['zip_code'] = self.validate(str(store['Zip']))
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['Phone'])
			item['latitude'] = self.validate(str(store['Latitude']))
			item['longitude'] = self.validate(str(store['Longitude']))
			item['store_hours'] = self.validate(store['Hours']).replace('to', '-')
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