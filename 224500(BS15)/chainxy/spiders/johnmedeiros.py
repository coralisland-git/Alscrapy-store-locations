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

class johnmedeiros(scrapy.Spider):
	name = 'johnmedeiros'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		for location in self.location_list:
			init_url = 'https://www.johnmedeiros.com/apps/stores/get_surrounding_stores.php?shop=john-medeiros-jewelry-collections.myshopify.com&latitude='+str(location['latitude'])+'&longitude='+str(location['longitude'])+'&max_distance=0&limit=100&calc_distance=1'
			yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = json.loads(response.body)
		for store in store_list['stores']:
			link = 'https://www.johnmedeiros.com/apps/stores/get_store_info.php?shop=john-medeiros-jewelry-collections.myshopify.com&data=detailed&store_id=%s' %store['store_id']
			yield scrapy.Request(url=link, callback=self.parse_page, meta = {'store_id':store['store_id'], 'latitude': store['lat'], 'longitude':store['lng']})

	def parse_page(self, response):
		detail = etree.HTML('<div>' + json.loads(response.body)['data'] + '</div>')
		try:
			item = ChainItem()
			item['store_name'] = self.validate(detail.xpath('//span[@class="name"]/text()')[0])
			item['store_number'] = response.meta['store_id']
			item['address'] = self.validate(detail.xpath('//span[@class="address"]/text()')[0])		
			try:
				item['city'] = self.validate(detail.xpath('//span[@class="city"]/text()')[0])
			except:
				pass
			try:
				item['state'] = self.validate(detail.xpath('//span[@class="prov_state"]/text()')[0])
			except:
				pass
			try:
				item['zip_code'] = self.validate(detail.xpath('//span[@class="postal_zip"]/text()')[0])
			except:
				pass
			item['country'] = 'United States'
			try:
				item['phone_number'] = self.validate(detail.xpath('//span[@class="phone"]/text()')[0])
			except:
				pass
			item['latitude'] = response.meta['latitude']
			item['longitude'] = response.meta['longitude']
			if item['address']+item['store_number'] not in self.history:
				self.history.append(item['address']+item['store_number'])
				yield item	
		except:
			pdb.set_trace()		

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''