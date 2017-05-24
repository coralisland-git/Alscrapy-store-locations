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

class wilco(scrapy.Spider):
	name = 'wilco'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.wilco.coop/wp-json/wp/v2/locations/?per_page=100'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['title']['rendered'])
			item['store_number'] = self.validate(store['store_number'])
			item['address'] = self.validate(store['address_address'])
			item['city'] = self.validate(store['address_city'])
			item['state'] = self.validate(store['address_state'])
			item['zip_code'] = self.validate(store['address_zipcode'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['options_phone'])
			item['latitude'] = self.validate(store['address_lat'])
			item['longitude'] = self.validate(store['address_lng'])
			item['store_hours'] = self.validate(store['store_services_hours'])
			item['store_type'] = self.validate(store['type'])
			yield item			


	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''