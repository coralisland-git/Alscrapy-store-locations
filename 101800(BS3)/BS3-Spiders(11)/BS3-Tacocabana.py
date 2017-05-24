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

class BS3Tacocabana(scrapy.Spider):
	name = 'BS3-Tacocabana'
	domain = 'https://www.tacocabana.com/'
	history = []

	def start_requests(self):
		
		init_url = 'http://www.tacocabana.com/wp-admin/admin-ajax.php?action=get_ajax_processor&processor=get-locations&queryType=&postID=816'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['post_title'])
			item['store_number'] = store['locator_store_number']
			item['address'] = self.validate(store['street_address_1'])
			item['address2'] = self.validate(store['street_address_2'])
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['zip_code']
			item['country'] = 'United States'
			item['phone_number'] = store['phone_number']
			item['latitude'] = store['x_coordinate']
			item['longitude'] = store['y_coordinate']
			item['store_hours'] = store['hours']
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] in self.history:
				continue
			self.history.append(item['store_number'])
			yield item			

	def validate(self, item):
		try:
			return item.strip().replace(';', ', ')
		except:
			return ''