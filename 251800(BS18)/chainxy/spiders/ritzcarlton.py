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
import pdb

class ritzcarlton(scrapy.Spider):
	name = 'ritzcarlton'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.ritzcarlton.com/en/hotels'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[@class="region"][1]//div[@class="sub-region"]//p//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//span[@class="property-name"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = self.validate(response.xpath('//abbr[@itemprop="addressCountry"]/text()').extract_first())
			item['phone_number'] = self.validate(response.xpath('//a[@itemprop="telephone"]/text()').extract_first())
			if len(item['zip_code']) > 6:
				item['state'] = item['zip_code'][:2].strip()
				item['zip_code'] = item['zip_code'][2:].strip()
			if item['address']+item['phone_number'] not in self.history and item['address'] != '':
				self.history.append(item['address']+item['phone_number'])
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