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

class candlewoodsuites(scrapy.Spider):
	name = 'candlewoodsuites'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'https://www.allstays.com/hotels-by-chain/candlewood-suites.htm'
		yield scrapy.Request(url=init_url, callback=self.parse_state)

	def parse_state(self, response):
		state_list = response.xpath('//a[@class="mapside button"]/@href').extract()
		for state in state_list : 
			state_link = 'https:' + state
			yield scrapy.Request(url=state_link, callback=self.parse_store)

	def parse_store(self, response):
		store_list = response.xpath('//a[@class="full-width button"]/@href').extract()
		if store_list:
			for store in store_list:
				store_link = 'https:' + store
				yield scrapy.Request(url=store_link, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//span[@itemprop="name"]/text()').extract_first())
			item['address'] = self.validate(response.xpath('//span[@itemprop="streetAddress"]//text()').extract_first())
			item['city'] = self.validate(response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first())
			item['state'] = self.validate(response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first())
			item['zip_code'] = self.validate(response.xpath('//span[@itemprop="postalCode"]/text()').extract_first())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()').extract_first())
			if item['store_name'] != '':
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