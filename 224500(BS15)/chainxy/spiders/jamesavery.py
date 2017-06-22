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

class jamesavery(scrapy.Spider):
	name = 'jamesavery'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.jamesavery.com/custserv/locate_store.cmd'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		data = response.body.split('var store = new Object();')[1]
		store = data
		store_list = response.body.split('var store = new Object();') 
		for store in store_list[1:]:
			try:
				item = ChainItem()
				item['store_name'] = self.get_value(store, 'store.STORE_NAME =')
				item['store_number'] = self.get_value(store, 'store.STORE_NUMBER =')
				item['address'] = self.get_value(store, 'store.ADDRESS_LINE_1 =')
				item['address2'] = self.get_value(store, 'store.ADDRESS_LINE_2 =')
				item['city'] = self.get_value(store, 'store.CITY =')
				item['state'] = self.get_value(store, 'store.STATE=')
				item['zip_code'] = self.get_value(store, 'store.ZIP_CODE =')
				item['country'] = self.get_value(store, 'store.COUNTRY_CODE=')
				item['phone_number'] = self.get_value(store, 'store.PHONE =')
				item['latitude'] = self.get_value(store, 'store.LATITUDE =')
				item['longitude'] = self.get_value(store, 'store.LONGITUDE =')
				yield item	
			except:
				pass

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

	def get_value(self, item, unit):
		try:
			return item.split(unit)[1].split(';')[0].strip().replace('"','').replace("'",'')
		except:
			return ''