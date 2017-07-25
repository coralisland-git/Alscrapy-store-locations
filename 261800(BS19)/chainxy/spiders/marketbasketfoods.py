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

class marketbasketfoods(scrapy.Spider):
	name = 'marketbasketfoods'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.marketbasketfoods.com/?sm-xml-search=1&lat=31.1616394&lng=-93.26953170000002&radius=0&namequery=31.1616393,%20-93.26953170000002&query_type=all&limit=0&sm_category=&sm_tag=&address=&city=&state=&zip=&pid=92'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['address'] = self.validate(store['address'])
				item['address2'] = self.validate(store['address2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['state'])
				item['zip_code'] = self.validate(store['zip'])
				item['country'] = self.validate(store['country'])
				item['phone_number'] = self.validate(store['phone'])
				item['latitude'] = self.validate(store['lat'])
				item['longitude'] = self.validate(store['lng'])
				item['store_hours'] = self.validate(store['post_content'])
				yield item	
			except:
				pass

	def validate(self, item):
		try:
			return item.strip().replace('<br class="" />','').replace('Hours:', '').replace('\n','')
		except:
			return ''

	def eliminate_space(self, items):
		tmp = []
		for item in items:
			if self.validate(item) != '':
				tmp.append(self.validate(item))
		return tmp