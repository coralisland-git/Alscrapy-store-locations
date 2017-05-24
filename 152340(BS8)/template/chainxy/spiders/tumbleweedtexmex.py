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

class tumbleweedtexmex(scrapy.Spider):
	name = 'tumbleweedtexmex'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://tumbleweedrestaurants.com/getAllLocationsNoLatLng.php'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")

		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['address'] = self.validate(store['address'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['latitude'])
			item['longitude'] = self.validate(store['longitude'])
			h_temp = ''
			week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
			for week in week_list:
				try:
					h_temp += week + ' ' + store['hours'][week] + ', '
				except:
					pass
			item['store_hours'] = h_temp[:-2]
			item['store_type'] = self.validate(store['storetype'])
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