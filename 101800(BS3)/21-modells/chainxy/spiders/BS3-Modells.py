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

class BS3Modells(scrapy.Spider):
	name = 'BS3-Modells'
	domain = 'https://www.modells.com'
	history = []

	def start_requests(self):
	
		init_url  = 'https://stores.modells.com/en/api/v2/stores.json'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['stores']
		for store in store_list:
			item = ChainItem()
			item['store_name'] = store['name']
			item['store_number'] = store['id']
			item['address'] = store['address_1']
			item['address2'] = store['address_2']
			item['city'] = store['city']
			item['state'] = store['state']
			item['zip_code'] = store['postal_code']
			item['country'] = store['country_code']
			item['phone_number'] = store['phone_number']
			item['latitude'] = store['latitude']
			item['longitude'] = store['longitude']
			h_temp = ''
			hour_list = store['regular_hour_ranges']
			for hour in hour_list:
				h_temp += self.validate(hour['days']) + ' ' + self.validate(hour['hours']) + ', '
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			if item['store_number'] in self.history:
				continue
			self.history.append(item['store_number'])
			yield item			

	def validate(self, item):
		try:
			return item.strip().replace('\n', '').replace('&#8211', '-').replace(';','')
		except:
			return ''