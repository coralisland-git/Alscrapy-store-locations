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
import time
import pdb
import unicodedata

class fields(scrapy.Spider):
	name = 'fields'
	domain = ''
	history = []

	def __init__(self):
		self.driver = webdriver.Chrome("./chromedriver")

	def start_requests(self):
		init_url = 'http://www.fields.ca/location.php'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		self.driver.get("http://www.fields.ca/location.php")
		time.sleep(5)
		source = self.driver.page_source.encode("utf8")
		with open('response.html', 'wb') as f:
			f.write(source)
		# store_list = response.xpath('//div[@class="resultlist result"]')
		# print('~~~~~~~~~~~~~~~~~~~~~~~~', len(store_list))
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