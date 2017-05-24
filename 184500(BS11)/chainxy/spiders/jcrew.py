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

class jcrew(scrapy.Spider):
	name = 'jcrew'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://stores.jcrew.com/en/api/v2/stores.json'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['stores']
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store['name'])
				item['store_number'] = self.validate(store['number'])
				item['address'] = self.validate(store['address_1'])
				item['address2'] = self.validate(store['address_2'])
				item['city'] = self.validate(store['city'])
				item['state'] = self.validate(store['state'])
				item['zip_code'] = self.validate(store['postal_code'])
				item['country'] = self.validate(store['country_code'])
				item['phone_number'] = self.validate(store['phone_number'])
				item['latitude'] = self.validate(str(store['latitude']))
				item['longitude'] = self.validate(str(store['longitude']))
				h_temp = ''
				hour_list = store['regular_hour_ranges']
				for hour in hour_list:
					h_temp += self.validate(hour['days']) + ' ' + self.validate(hour['hours']).replace('&#8211;', '-')+ ', '
				item['store_hours'] = h_temp[:-2]
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