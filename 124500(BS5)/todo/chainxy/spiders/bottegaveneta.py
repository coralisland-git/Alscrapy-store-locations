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
import unicodedata

class bottegaveneta(scrapy.Spider):
	name = 'bottegaveneta'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.bottegaveneta.com/experience/us/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)
		print("=========  Checking.......", len(store_list))
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['post_title'])
			item['store_number'] = self.validate(str(store['ID']))
			item['address'] = self.format(store['wpcf-yoox-store-address'])
			item['city'] = self.validate(store['wpcf-city'])
			try:
				item['country'] = self.validate(store['location']['country']['name'])
			except:
				item['country'] = self.validate(store['wpcf-yoox-store-country-iso'])
			try:
				item['phone_number'] = self.validate(store['wpcf-yoox-store-phone'])
			except:
				pass
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			item['store_hours'] = self.validate(store['wpcf-yoox-store-hours'])
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item			

	def validate(self, item):
		try:
			return item.strip().replace('\n', '').replace('\t','').replace('\r','')
		except:
			return ''

	def format(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''