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

class shopnsavefood(scrapy.Spider):
	name = 'shopnsavefood'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.shopnsavefood.com/DesktopModules/StoreLocator/API/StoreWebAPI.asmx/GetAllStores'
		header = {
			"Accept":"application/json, text/plain, */*",
			"Accept-Encoding":"gzip, deflate, sdch, br",
			"Content-Type":"application/json; charset=utf-8"
		}
		yield scrapy.Request(url=init_url, headers=header, method='get', callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['d']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['Name'])
			item['store_number'] = self.validate(str(store['StoreID']))
			item['address'] = self.validate(store['Address1'])
			item['address2'] = self.validate(store['Address2'])
			item['city'] = self.validate(store['City'])
			item['state'] = self.validate(store['State'])
			item['zip_code'] = self.validate(store['Zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['Phone'])
			item['latitude'] = self.validate(store['Latitude'])
			item['longitude'] = self.validate(store['Longitude'])
			item['store_hours'] = self.validate(store['Hours'])
			if self.validate(store['Hours2']) != '':
				item['store_hours'] += ', ' + self.validate(store['Hours2'])
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

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''