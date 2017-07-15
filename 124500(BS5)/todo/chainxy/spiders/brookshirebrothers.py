
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

class brookshirebrothers(scrapy.Spider):
	name = 'brookshirebrothers'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'https://www.brookshirebrothers.com/store-locator?ajax=1'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		data = response.body.split('var locationCoordinates =')[1].strip()[:-9].strip()
		store_list = data.split('type:"Feature",')
		for store in store_list[1:]:
			store = store.split('keywords')[0].strip()
			item = ChainItem()
			item['store_name'] = self.get_value(store, 'title:')
			item['address'] = self.get_value(store, 'address:')
			item['city'] = self.get_value(store, 'locality:').split(',')[0].strip()
			item['state'] = self.get_value(store, 'locality:').split(',')[1].split('<span>')[0].strip()
			item['zip_code'] = self.get_value(store, 'locality:').split(',')[1].split('<span>')[1].split('</span>')[0].strip()
			item['country'] = 'United States'
			item['phone_number'] = self.get_value(store, 'tel:')
			item['latitude'] = self.get_value(store, 'coordinates:').split(',')[0]
			item['longitude'] = self.get_value(store, 'coordinates:').split(',')[1].split('"')[0]
			if item['address']+item['phone_number'] not in self.history:
				self.history.append(item['address']+item['phone_number'])
				yield item	
			
	def get_value(self, item, params):
		try:
			item = item.split(params)[1].split('",')[0].strip()[1:]
			return item
		except:
			return ''

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''