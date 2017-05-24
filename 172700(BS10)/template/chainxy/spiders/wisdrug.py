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

class wisdrug(scrapy.Spider):
	name = 'wisdrug'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.lewisdrug.com/stores/store-finder'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="entries"]//div[@class="entry"]')
		for store in store_list:
			item = ChainItem()
			item['address'] = self.validate(store.xpath('.//h3[@class="map-address"]/text()').extract_first())		
			item['city'] = self.validate(store.xpath('.//span[@class="map-city"]/text()').extract_first())
			item['state'] = self.validate(store.xpath('.//span[@class="map-state"]/text()').extract_first())
			item['zip_code'] = self.validate(store.xpath('.//span[@class="map-zip"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//span[@class="map-phone"]//a/text()').extract_first())
			geolocation = self.validate(store.xpath('./@location').extract_first()).split(',')
			item['latitude'] = geolocation[0]
			item['longitude'] = geolocation[1]
			item['store_hours'] = self.validate(store.xpath('.//span[@class="entry-data"]/text()').extract_first())
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