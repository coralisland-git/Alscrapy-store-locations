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

class smallcakes(scrapy.Spider):
	name = 'smallcakes'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.smallcakescupcakery.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@id="location-list"]//div[@class="location-item"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//span[@class="location-locale"]/text()').extract_first())
				item['address'] = self.validate(store.xpath('.//span[@class="location-address"]/text()').extract_first())				
				item['city'] = self.validate(store.xpath('.//span[@class="location-city"]/text()').extract_first())				
				item['state'] = self.validate(store.xpath('.//span[@class="location-state"]/text()').extract_first())				
				item['zip_code'] = self.validate(store.xpath('.//span[@class="location-zip"]/text()').extract_first())				
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//span[@class="phone"]//a/text()').extract_first())				
				item['coming_soon'] = '0'
				if 'coming' in item['store_name'].lower():
					item['coming_soon'] = '1'
					item['store_name'] = self.validate(item['store_name'].split('--')[0])
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