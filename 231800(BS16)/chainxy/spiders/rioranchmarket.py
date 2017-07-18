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
import usaddress

class rioranchmarket(scrapy.Spider):
	name = 'rioranchmarket'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.rioranchmarket.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="entries locations"]//div[@class="location"]')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//h4//a/text()').extract_first())
				item['store_number'] = ''
				if '#' in item['store_name']:
					item['store_name'] = self.validate(store.xpath('.//h4//a/text()').extract_first()).split('#')[0].strip()
					item['store_number'] = self.validate(store.xpath('.//h4//a/text()').extract_first()).split('#')[1].strip()
				item['address'] = self.validate(store.xpath('.//span[@itemprop="address"]/text()').extract_first())
				item['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first())
				item['state'] = self.validate(store.xpath('.//span[@itemprop="addressRegion"]/text()').extract_first())
				item['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]/text()').extract_first())
				item['country'] = 'United States'
				item['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]//a/text()').extract_first())
				if item['store_number'] != '':
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