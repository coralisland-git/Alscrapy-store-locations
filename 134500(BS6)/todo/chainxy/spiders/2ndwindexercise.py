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

class secondwindexercise(scrapy.Spider):
	name = '2ndwindexercise'
	domain = 'https://www.2ndwindexercise.com/'
	history = []

	def start_requests(self):
		init_url = 'https://www.2ndwindexercise.com/storepickup/index/loadstore/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)['storesjson']
		for store in store_list:
			detail_url = self.domain + self.validate(store['rewrite_request_path'])
			request = scrapy.Request(url=detail_url, callback=self.parse_page)
			request.meta['store_name'] = self.validate(store['store_name'])
			request.meta['address'] = self.validate(store['address'])
			request.meta['city'] = self.validate(store['city'])
			request.meta['state'] = self.validate(store['state'])
			request.meta['country'] = 'United States'
			request.meta['phone_number'] = self.validate(store['phone'])
			request.meta['latitude'] = self.validate(store['latitude'])
			request.meta['longitude'] = self.validate(store['longitude'])
			yield request

	def parse_page(self, response):
		item = ChainItem()
		h_temp =''
		hour_list = response.xpath('//div[@class="open_hour"]//tr')
		for hour in hour_list:
			h_temp += self.validate(hour.xpath('.//td[1]/text()').extract_first()) + ' ' + self.validate(hour.xpath('.//td[3]/text()').extract_first()) + ', '
		item['store_hours'] = h_temp[:-2]
		item['store_name'] = response.meta['store_name']
		item['address'] = response.meta['address']
		item['city'] = response.meta['city']
		item['state'] = response.meta['state']
		item['country'] = response.meta['country']
		item['phone_number'] = response.meta['phone_number']
		item['latitude'] = response.meta['latitude']
		item['longitude'] =response.meta['longitude']
		yield item


	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''